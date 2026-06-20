# ============================================================
#  analytics/recommendation_engine.py  —  Skill Gap & Recommendations
# ============================================================

from database.db_manager import DatabaseManager


class RecommendationEngine:
    """
    Takes a candidate's current skills and produces:
    - Skill gap analysis
    - High-value skills to learn next
    - Best matching job types
    - Salary uplift potential
    """

    def __init__(self, db: DatabaseManager):
        self.db = db

    def analyse(self, candidate_skills: list[str], experience_level: str = "Mid-level") -> dict:
        """
        Full recommendation report for a candidate.

        Parameters
        ----------
        candidate_skills   : list of skill names the candidate already has
        experience_level   : "Junior" | "Mid-level" | "Senior" | "Manager"

        Returns
        -------
        dict with keys: matched_jobs, skill_gap, recommended_skills, salary_potential
        """
        candidate_skills_lower = [s.lower().strip() for s in candidate_skills]

        matched_jobs    = self._find_matching_jobs(candidate_skills_lower, experience_level)
        market_top      = self._get_top_market_skills(30)
        skill_gap       = self._compute_gap(candidate_skills_lower, market_top)
        recommended     = self._prioritise_recommendations(skill_gap)
        salary_potential = self._salary_potential(candidate_skills_lower, skill_gap[:5])

        return {
            "input": {
                "candidate_skills":   candidate_skills_lower,
                "experience_level":   experience_level,
            },
            "matched_jobs":        matched_jobs,
            "skill_gap":           skill_gap,
            "recommended_skills":  recommended,
            "salary_potential":    salary_potential,
        }

    # ── Private Helpers ───────────────────────────────────────
    def _find_matching_jobs(self, skills: list[str], exp_level: str) -> list[dict]:
        """Jobs that match at least 2 of the candidate's skills."""
        if not skills:
            return []
        placeholders = ", ".join(["%s"] * len(skills))
        sql = f"""
            SELECT jp.job_id, jp.title, jp.company, jp.city, jp.salary_avg,
                   jp.is_remote, jp.experience_level, jp.url,
                   COUNT(DISTINCT js.skill) AS matched_skills
            FROM   job_postings jp
            JOIN   job_skills   js ON jp.job_id = js.job_id
            WHERE  js.skill IN ({placeholders})
              AND  jp.experience_level = %s
            GROUP  BY jp.job_id, jp.title, jp.company, jp.city,
                      jp.salary_avg, jp.is_remote, jp.experience_level, jp.url
            HAVING COUNT(DISTINCT js.skill) >= 2
            ORDER  BY matched_skills DESC
            LIMIT  10
        """
        return self.db.fetch_all(sql, tuple(skills) + (exp_level,))

    def _get_top_market_skills(self, limit: int) -> list[dict]:
        return self.db.fetch_all(
            "SELECT skill, demand_count FROM v_top_skills LIMIT %s", (limit,)
        )

    def _compute_gap(self, candidate_skills: list[str], market_skills: list[dict]) -> list[dict]:
        """Skills in top market demand that the candidate doesn't have."""
        gap = []
        for row in market_skills:
            if row["skill"] not in candidate_skills:
                gap.append(row)
        return gap

    def _prioritise_recommendations(self, gap_skills: list[dict]) -> list[dict]:
        """
        Enrich gap skills with salary data and sort by combined score
        (demand + salary potential).
        """
        if not gap_skills:
            return []
        skill_names = [r["skill"] for r in gap_skills]
        placeholders = ", ".join(["%s"] * len(skill_names))
        salary_map = {}
        try:
            rows = self.db.fetch_all(
                f"SELECT skill, avg_salary FROM v_skill_salary WHERE skill IN ({placeholders})",
                tuple(skill_names),
            )
            salary_map = {r["skill"]: r["avg_salary"] for r in rows}
        except Exception:
            pass

        enriched = []
        for row in gap_skills:
            avg_sal = salary_map.get(row["skill"])
            enriched.append({
                "skill":        row["skill"],
                "demand_count": row["demand_count"],
                "avg_salary":   float(avg_sal) if avg_sal else None,
            })

        # Sort by demand first, then salary
        enriched.sort(key=lambda x: (x["demand_count"], x["avg_salary"] or 0), reverse=True)
        return enriched[:10]

    def _salary_potential(self, current_skills: list[str], top_gap: list[dict]) -> dict:
        """Estimate current vs potential salary after adding gap skills."""
        # Current salary range based on existing skills
        current_avg = self._avg_salary_for_skills(current_skills)
        gap_names   = [r["skill"] for r in top_gap]
        future_avg  = self._avg_salary_for_skills(current_skills + gap_names)

        return {
            "current_avg_salary":      current_avg,
            "potential_avg_salary":    future_avg,
            "estimated_uplift":        round((future_avg or 0) - (current_avg or 0), 2),
            "skills_to_add":           gap_names,
        }

    def _avg_salary_for_skills(self, skills: list[str]) -> float | None:
        if not skills:
            return None
        placeholders = ", ".join(["%s"] * len(skills))
        row = self.db.fetch_one(
            f"""SELECT ROUND(AVG(jp.salary_avg), 0) AS avg_sal
                FROM job_postings jp
                JOIN job_skills   js ON jp.job_id = js.job_id
                WHERE js.skill IN ({placeholders})
                  AND jp.salary_avg IS NOT NULL""",
            tuple(skills),
        )
        return float(row["avg_sal"]) if row and row["avg_sal"] else None
