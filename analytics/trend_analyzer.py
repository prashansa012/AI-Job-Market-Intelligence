# ============================================================
#  analytics/trend_analyzer.py  —  Hiring Trend Analyzer (MySQL)
# ============================================================

from database.db_manager import DatabaseManager


class TrendAnalyzer:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def top_skills(self, limit: int = 20) -> list[dict]:
        return self.db.fetch_all(
            "SELECT skill, demand_count, demand_pct FROM v_top_skills LIMIT %s",
            (limit,),
        )

    def city_hiring(self, limit: int = 15) -> list[dict]:
        return self.db.fetch_all(
            "SELECT city, country, total_jobs, avg_salary, remote_jobs FROM v_city_hiring LIMIT %s",
            (limit,),
        )

    def remote_vs_onsite(self) -> list[dict]:
        return self.db.fetch_all(
            "SELECT is_remote, job_count, percentage, avg_salary FROM v_remote_vs_onsite"
        )

    def experience_demand(self) -> list[dict]:
        return self.db.fetch_all(
            "SELECT experience_level, job_count, avg_salary FROM v_experience_demand"
        )

    def skill_salary(self, limit: int = 20) -> list[dict]:
        return self.db.fetch_all(
            "SELECT skill, avg_salary, min_salary, max_salary, job_count, salary_rank FROM v_skill_salary LIMIT %s",
            (limit,),
        )

    def monthly_posting_trend(self) -> list[dict]:
        # MySQL: DATE_FORMAT instead of TO_CHAR, DATE_SUB instead of INTERVAL syntax
        return self.db.fetch_all("""
            SELECT DATE_FORMAT(posted_date, '%Y-%m')  AS month,
                   COUNT(*)                           AS job_count,
                   ROUND(AVG(salary_avg), 0)          AS avg_salary
            FROM   job_postings
            WHERE  posted_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP  BY month
            ORDER  BY month
        """)

    def source_breakdown(self) -> list[dict]:
        return self.db.fetch_all("""
            SELECT source,
                   COUNT(*) AS job_count,
                   ROUND(AVG(salary_avg), 0) AS avg_salary
            FROM   job_postings
            GROUP  BY source
            ORDER  BY job_count DESC
        """)

    def skill_group_demand(self) -> list[dict]:
        return self.db.fetch_all("""
            SELECT skill_group,
                   COUNT(*)               AS demand_count,
                   COUNT(DISTINCT job_id) AS unique_jobs
            FROM   job_skills
            GROUP  BY skill_group
            ORDER  BY demand_count DESC
        """)

    def full_dashboard(self) -> dict:
        total = self.db.get_total_jobs()
        return {
            "summary":            {"total_jobs_collected": total},
            "top_skills":         self.top_skills(),
            "city_hiring":        self.city_hiring(),
            "remote_vs_onsite":   self.remote_vs_onsite(),
            "experience_demand":  self.experience_demand(),
            "skill_salary":       self.skill_salary(),
            "monthly_trend":      self.monthly_posting_trend(),
            "source_breakdown":   self.source_breakdown(),
            "skill_group_demand": self.skill_group_demand(),
        }
