# ============================================================
#  config/settings.py  —  Central Configuration (MySQL)
# ============================================================

# ── Database ─────────────────────────────────────────────────
DB_CONFIG={
    "host": "localhost",
    "port": 3306, 
    "database": "job_market_db",
    "user": "root",
    "password":"Admin"
}

# ── API Keys  ─────────────────────────────────────────────────
ADZUNA_APP_ID  = "260d10ef"   # https://developer.adzuna.com
ADZUNA_API_KEY = "ba00b65460777ee4c2f7932af5f1462e"
MUSE_API_KEY   = "your_muse_api_key"    # https://www.themuse.com/developers/api/v2
# RemoteOK is free — no key needed

# ── Collection Settings ───────────────────────────────────────
ADZUNA_COUNTRY      = "in"          # in = India, gb = UK, us = USA
ADZUNA_RESULTS_PAGE = 50
MAX_PAGES_PER_RUN   = 5
MUSE_PAGE_SIZE      = 20

# ── Export Paths ──────────────────────────────────────────────
EXPORT_DIR       = "reports/"
DASHBOARD_JSON   = "reports/dashboard.json"
SALARY_CSV       = "reports/salary_intelligence.csv"
SKILLS_CSV       = "reports/top_skills.csv"
TRENDS_CSV       = "reports/hiring_trends.csv"

# ── Skill Keywords (used by SkillExtractor) ───────────────────
SKILL_KEYWORDS = [
    # Programming
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "kotlin", "swift", "php", "ruby", "scala", "r", "matlab",
    # Web
    "react", "angular", "vue", "node.js", "django", "flask", "fastapi",
    "spring", "laravel", "express", "next.js", "nuxt",
    # Data / AI
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "machine learning", "deep learning", "nlp", "computer vision",
    "data science", "big data", "spark", "hadoop", "kafka",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "ci/cd", "jenkins", "github actions", "linux",
    # Mobile
    "android", "ios", "flutter", "react native",
    # Business / Other
    "excel", "power bi", "tableau", "communication", "leadership",
    "agile", "scrum", "jira", "git",
]
