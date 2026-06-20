# ============================================================
#  analytics/skill_extractor.py  —  Regex-based Skill Extractor
# ============================================================

import re
from config.settings import SKILL_KEYWORDS

# Skill → Category mapping
SKILL_GROUPS = {
    "python": "Programming", "java": "Programming", "javascript": "Programming",
    "typescript": "Programming", "c++": "Programming", "c#": "Programming",
    "go": "Programming", "rust": "Programming", "kotlin": "Programming",
    "swift": "Programming", "php": "Programming", "ruby": "Programming",
    "scala": "Programming", "r": "Programming", "matlab": "Programming",

    "react": "Web", "angular": "Web", "vue": "Web", "node.js": "Web",
    "django": "Web", "flask": "Web", "fastapi": "Web", "spring": "Web",
    "laravel": "Web", "express": "Web", "next.js": "Web", "nuxt": "Web",

    "sql": "Database", "postgresql": "Database", "mysql": "Database",
    "mongodb": "Database", "redis": "Database", "elasticsearch": "Database",

    "pandas": "Data/AI", "numpy": "Data/AI", "scikit-learn": "Data/AI",
    "tensorflow": "Data/AI", "pytorch": "Data/AI", "keras": "Data/AI",
    "machine learning": "Data/AI", "deep learning": "Data/AI",
    "nlp": "Data/AI", "computer vision": "Data/AI", "data science": "Data/AI",
    "big data": "Data/AI", "spark": "Data/AI", "hadoop": "Data/AI", "kafka": "Data/AI",

    "aws": "Cloud/DevOps", "azure": "Cloud/DevOps", "gcp": "Cloud/DevOps",
    "docker": "Cloud/DevOps", "kubernetes": "Cloud/DevOps",
    "terraform": "Cloud/DevOps", "ansible": "Cloud/DevOps",
    "ci/cd": "Cloud/DevOps", "jenkins": "Cloud/DevOps",
    "github actions": "Cloud/DevOps", "linux": "Cloud/DevOps",

    "android": "Mobile", "ios": "Mobile", "flutter": "Mobile",
    "react native": "Mobile",

    "excel": "Business", "power bi": "Business", "tableau": "Business",
    "agile": "Business", "scrum": "Business", "jira": "Business",
    "git": "Business", "communication": "Business", "leadership": "Business",
}


class SkillExtractor:
    """
    Extracts skills from job descriptions using compiled regex patterns.
    Multi-word skills (e.g. 'machine learning') are matched before single words.
    """

    def __init__(self):
        # Sort so longer phrases match first
        sorted_skills = sorted(SKILL_KEYWORDS, key=len, reverse=True)
        self._patterns = {
            skill: re.compile(
                r"(?<![a-zA-Z0-9_/])" + re.escape(skill) + r"(?![a-zA-Z0-9_/])",
                re.IGNORECASE,
            )
            for skill in sorted_skills
        }

    def extract(self, job_id: str, description: str) -> list[dict]:
        """
        Extract all skills from a job description.
        Returns list of {job_id, skill, skill_group} dicts.
        """
        if not description:
            return []

        found = []
        seen  = set()
        for skill, pattern in self._patterns.items():
            if pattern.search(description) and skill not in seen:
                seen.add(skill)
                found.append({
                    "job_id":     job_id,
                    "skill":      skill.lower(),
                    "skill_group": SKILL_GROUPS.get(skill.lower(), "Other"),
                })
        return found

    def extract_bulk(self, jobs: list[dict]) -> list[dict]:
        """Extract skills for a list of job dicts."""
        all_skills = []
        for job in jobs:
            skills = self.extract(job["job_id"], job.get("description", ""))
            all_skills.extend(skills)
        return all_skills

    def count_skills(self, skill_rows: list[dict]) -> dict:
        """Return {skill: count} from extracted skill rows."""
        counts = {}
        for row in skill_rows:
            counts[row["skill"]] = counts.get(row["skill"], 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
