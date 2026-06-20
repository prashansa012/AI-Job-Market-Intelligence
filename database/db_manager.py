# ============================================================
#  database/db_manager.py  —  MySQL Database Manager
# ============================================================

import mysql.connector
from mysql.connector import errorcode
from config.settings import DB_CONFIG


class DatabaseManager:
    """Handles all database operations — connect, create, insert, query."""

    def __init__(self):
        self.conn   = None
        self.cursor = None

    # ── Connection ────────────────────────────────────────────
    def connect(self):
        try:
            self.conn   = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True)
            print("[DB] Connected to MySQL successfully.")
        except mysql.connector.Error as e:
            raise ConnectionError(f"[DB] Connection failed: {e}")

    def disconnect(self):
        if self.cursor: self.cursor.close()
        if self.conn:   self.conn.close()
        print("[DB] Disconnected.")

    def commit(self):
        self.conn.commit()

    # ── Schema Setup ──────────────────────────────────────────
    def create_tables(self):
        """Create all tables if they don't exist."""
        statements = [
            """
            CREATE TABLE IF NOT EXISTS job_postings (
                id               INT AUTO_INCREMENT PRIMARY KEY,
                job_id           VARCHAR(255) UNIQUE,
                title            VARCHAR(500),
                company          VARCHAR(300),
                location         VARCHAR(300),
                city             VARCHAR(150),
                country          VARCHAR(100),
                salary_min       DECIMAL(12,2),
                salary_max       DECIMAL(12,2),
                salary_avg       DECIMAL(12,2),
                description      TEXT,
                job_type         VARCHAR(100),
                is_remote        BOOLEAN DEFAULT FALSE,
                experience_level VARCHAR(100),
                source           VARCHAR(100),
                url              VARCHAR(1000),
                posted_date      DATE,
                collected_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS job_skills (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                job_id      VARCHAR(255),
                skill       VARCHAR(200),
                skill_group VARCHAR(100),
                UNIQUE KEY uq_job_skill (job_id, skill),
                FOREIGN KEY (job_id) REFERENCES job_postings(job_id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS salary_intelligence (
                id            INT AUTO_INCREMENT PRIMARY KEY,
                skill         VARCHAR(200),
                avg_salary    DECIMAL(12,2),
                min_salary    DECIMAL(12,2),
                max_salary    DECIMAL(12,2),
                job_count     INT,
                recorded_date DATE DEFAULT (CURRENT_DATE)
            )
            """,
        ]
        for sql in statements:
            self.cursor.execute(sql)
        self.commit()
        print("[DB] Tables created / verified.")

    def create_views(self):
        """Create analytical SQL Views."""
        views = {
            "v_top_skills": """
                SELECT skill,
                       COUNT(*)                                          AS demand_count,
                       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS demand_pct
                FROM   job_skills
                GROUP  BY skill
                ORDER  BY demand_count DESC
            """,
            "v_city_hiring": """
                SELECT city,
                       country,
                       COUNT(*)                          AS total_jobs,
                       ROUND(AVG(salary_avg), 0)         AS avg_salary,
                       SUM(CASE WHEN is_remote THEN 1 ELSE 0 END) AS remote_jobs
                FROM   job_postings
                WHERE  city IS NOT NULL
                GROUP  BY city, country
                ORDER  BY total_jobs DESC
            """,
            "v_remote_vs_onsite": """
                SELECT is_remote,
                       COUNT(*)                                          AS job_count,
                       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage,
                       ROUND(AVG(salary_avg), 0)                          AS avg_salary
                FROM   job_postings
                GROUP  BY is_remote
            """,
            "v_experience_demand": """
                SELECT experience_level,
                       COUNT(*)                 AS job_count,
                       ROUND(AVG(salary_avg), 0) AS avg_salary
                FROM   job_postings
                WHERE  experience_level IS NOT NULL
                GROUP  BY experience_level
                ORDER  BY job_count DESC
            """,
            "v_skill_salary": """
                SELECT js.skill,
                       ROUND(AVG(jp.salary_avg), 0)   AS avg_salary,
                       ROUND(MIN(jp.salary_min), 0)   AS min_salary,
                       ROUND(MAX(jp.salary_max), 0)   AS max_salary,
                       COUNT(DISTINCT jp.job_id)       AS job_count,
                       RANK() OVER (ORDER BY AVG(jp.salary_avg) DESC) AS salary_rank
                FROM   job_skills js
                JOIN   job_postings jp ON js.job_id = jp.job_id
                WHERE  jp.salary_avg IS NOT NULL
                GROUP  BY js.skill
                HAVING COUNT(*) >= 3
                ORDER  BY avg_salary DESC
            """,
        }
        for view_name, select_sql in views.items():
            self.cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
            self.cursor.execute(f"CREATE VIEW {view_name} AS {select_sql}")
        self.commit()
        print("[DB] Views created / updated.")

    def create_stored_procedures(self):
        """Create stored procedures for analytics."""
        self.cursor.execute("DROP PROCEDURE IF EXISTS refresh_salary_intelligence")
        self.cursor.execute("""
            CREATE PROCEDURE refresh_salary_intelligence()
            BEGIN
                DELETE FROM salary_intelligence
                WHERE recorded_date = CURDATE();

                INSERT INTO salary_intelligence (skill, avg_salary, min_salary, max_salary, job_count)
                SELECT js.skill,
                       AVG(jp.salary_avg),
                       MIN(jp.salary_min),
                       MAX(jp.salary_max),
                       COUNT(DISTINCT jp.job_id)
                FROM   job_skills js
                JOIN   job_postings jp ON js.job_id = jp.job_id
                WHERE  jp.salary_avg IS NOT NULL
                GROUP  BY js.skill
                HAVING COUNT(*) >= 2;
            END
        """)
        self.commit()
        print("[DB] Stored procedures created.")

    # ── Insert ────────────────────────────────────────────────
    def insert_jobs(self, jobs: list[dict]) -> int:
        """Bulk insert job postings. Returns count inserted."""
        if not jobs:
            return 0
        columns = [
            "job_id", "title", "company", "location", "city", "country",
            "salary_min", "salary_max", "salary_avg", "description",
            "job_type", "is_remote", "experience_level", "source", "url", "posted_date",
        ]
        sql = f"""
            INSERT IGNORE INTO job_postings ({', '.join(columns)})
            VALUES ({', '.join(['%s'] * len(columns))})
        """
        rows = [tuple(job.get(col) for col in columns) for job in jobs]
        self.cursor.executemany(sql, rows)
        self.commit()
        return self.cursor.rowcount

    def insert_skills(self, skill_rows: list[dict]) -> int:
        """Insert extracted skills for jobs."""
        if not skill_rows:
            return 0
        sql = """
            INSERT IGNORE INTO job_skills (job_id, skill, skill_group)
            VALUES (%s, %s, %s)
        """
        rows = [(r["job_id"], r["skill"], r["skill_group"]) for r in skill_rows]
        self.cursor.executemany(sql, rows)
        self.commit()
        return self.cursor.rowcount

    # ── Queries ───────────────────────────────────────────────
    def fetch_all(self, sql: str, params=None) -> list[dict]:
        self.cursor.execute(sql, params or ())
        return self.cursor.fetchall()

    def fetch_one(self, sql: str, params=None) -> dict | None:
        self.cursor.execute(sql, params or ())
        return self.cursor.fetchone()

    def call_procedure(self, name: str):
        self.cursor.callproc(name)
        self.commit()

    def get_total_jobs(self) -> int:
        row = self.fetch_one("SELECT COUNT(*) AS c FROM job_postings")
        return row["c"] if row else 0
