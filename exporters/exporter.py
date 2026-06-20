# ============================================================
#  exporters/exporter.py  —  JSON Dashboard & CSV Reports
# ============================================================

import json
import csv
import os
from datetime import date
from config.settings import EXPORT_DIR, DASHBOARD_JSON, SALARY_CSV, SKILLS_CSV, TRENDS_CSV


def _ensure_dir():
    os.makedirs(EXPORT_DIR, exist_ok=True)


class DashboardExporter:
    """Exports full analytics dashboard to a JSON file."""

    def export(self, dashboard: dict) -> str:
        _ensure_dir()
        dashboard["generated_at"] = date.today().isoformat()
        with open(DASHBOARD_JSON, "w", encoding="utf-8") as f:
            json.dump(dashboard, f, indent=2, default=str)
        print(f"[Export] Dashboard JSON → {DASHBOARD_JSON}")
        return DASHBOARD_JSON


class CSVExporter:
    """Exports individual analytics tables to CSV files."""

    def export_skills(self, skill_rows: list[dict]) -> str:
        return self._write_csv(SKILLS_CSV, skill_rows, ["skill", "demand_count", "demand_pct"])

    def export_salary(self, salary_rows: list[dict]) -> str:
        return self._write_csv(
            SALARY_CSV, salary_rows,
            ["skill", "avg_salary", "min_salary", "max_salary", "job_count", "salary_rank"],
        )

    def export_trends(self, trend_rows: list[dict]) -> str:
        return self._write_csv(TRENDS_CSV, trend_rows, ["month", "job_count", "avg_salary"])

    def export_recommendations(self, rec: dict, filename: str = None) -> str:
        _ensure_dir()
        path = filename or f"{EXPORT_DIR}recommendations_{date.today().isoformat()}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=2, default=str)
        print(f"[Export] Recommendations → {path}")
        return path

    @staticmethod
    def _write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> str:
        _ensure_dir()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        print(f"[Export] CSV → {path}  ({len(rows)} rows)")
        return path
