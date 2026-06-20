#!/usr/bin/env python3
# ============================================================
#  main.py  —  AI-Powered Job Market Intelligence System
#              Main Orchestrator — Run this file to start
# ============================================================

import sys
from database.db_manager        import DatabaseManager
from collectors.adzuna_collector  import AdzunaCollector
from collectors.remoteok_collector import RemoteOKCollector
from collectors.muse_collector    import MuseCollector
from analytics.skill_extractor   import SkillExtractor
from analytics.trend_analyzer    import TrendAnalyzer
from analytics.recommendation_engine import RecommendationEngine
from exporters.exporter          import DashboardExporter, CSVExporter


# ── Pretty Banner ─────────────────────────────────────────────
BANNER = """
╔══════════════════════════════════════════════════════════╗
║   AI-Powered Job Market Intelligence System  v1.0        ║
║   Collectors: Adzuna | RemoteOK | TheMuse                ║
╚══════════════════════════════════════════════════════════╝
"""


def setup_database(db: DatabaseManager):
    """Create schema, views, stored procedures."""
    print("\n[Step 1] Setting up database schema ...")
    db.create_tables()
    db.create_views()
    db.create_stored_procedures()


def collect_jobs(db: DatabaseManager) -> int:
    """Collect from all 3 APIs and store in DB."""
    print("\n[Step 2] Collecting job postings from APIs ...")

    all_jobs = []

    # Adzuna
    try:
        adzuna_jobs = AdzunaCollector().collect(
            keywords=["python developer", "data scientist",
                      "machine learning engineer", "software engineer",
                      "devops engineer", "react developer"]
        )
        all_jobs.extend(adzuna_jobs)
    except Exception as e:
        print(f"  [Warning] Adzuna failed: {e}")

    # RemoteOK (free, no key)
    try:
        remoteok_jobs = RemoteOKCollector().collect()
        all_jobs.extend(remoteok_jobs)
    except Exception as e:
        print(f"  [Warning] RemoteOK failed: {e}")

    # The Muse
    try:
        muse_jobs = MuseCollector().collect(pages=3)
        all_jobs.extend(muse_jobs)
    except Exception as e:
        print(f"  [Warning] TheMuse failed: {e}")

    if not all_jobs:
        print("  [Warning] No jobs collected. Check API keys in config/settings.py")
        return 0

    inserted = db.insert_jobs(all_jobs)
    print(f"\n  → Total collected: {len(all_jobs)} | Newly inserted: {inserted}")
    return len(all_jobs)


def extract_and_store_skills(db: DatabaseManager):
    """Run regex skill extraction on all job descriptions."""
    print("\n[Step 3] Extracting skills from job descriptions ...")

    jobs = db.fetch_all(
        "SELECT job_id, description FROM job_postings WHERE job_id NOT IN (SELECT DISTINCT job_id FROM job_skills)"
    )
    if not jobs:
        print("  No new jobs to process for skill extraction.")
        return

    extractor  = SkillExtractor()
    skill_rows = extractor.extract_bulk(jobs)
    inserted   = db.insert_skills(skill_rows)
    print(f"  → Skill rows inserted: {inserted}")

    # Refresh salary intelligence via stored procedure
    db.call_procedure("refresh_salary_intelligence")
    print("  → Salary intelligence refreshed")


def run_analytics_and_export(db: DatabaseManager):
    """Run trend analysis and export all reports."""
    print("\n[Step 4] Running analytics & exporting reports ...")

    analyzer  = TrendAnalyzer(db)
    dashboard = analyzer.full_dashboard()

    # JSON Dashboard
    DashboardExporter().export(dashboard)

    # CSV Reports
    csv_exp = CSVExporter()
    csv_exp.export_skills(dashboard["top_skills"])
    csv_exp.export_salary(dashboard["skill_salary"])
    csv_exp.export_trends(dashboard["monthly_trend"])

    # Print summary to console
    print("\n" + "─" * 55)
    print("  📊  MARKET INTELLIGENCE SUMMARY")
    print("─" * 55)
    print(f"  Total Jobs in DB : {dashboard['summary']['total_jobs_collected']}")

    print("\n  🔥 Top 5 In-Demand Skills:")
    for row in dashboard["top_skills"][:5]:
        bar = "█" * int(row["demand_pct"] or 0)
        print(f"     {row['skill']:<20} {row['demand_count']:>5} jobs  {bar}")

    print("\n  💰 Top 5 Highest Paying Skills:")
    for row in dashboard["skill_salary"][:5]:
        sal = f"${row['avg_salary']:,.0f}" if row["avg_salary"] else "N/A"
        print(f"     {row['skill']:<20} {sal}")

    print("\n  🏙️  Top 5 Hiring Cities:")
    for row in dashboard["city_hiring"][:5]:
        print(f"     {row['city']:<25} {row['total_jobs']:>4} jobs")

    print("\n  🌐 Remote vs Onsite:")
    for row in dashboard["remote_vs_onsite"]:
        label = "Remote " if row["is_remote"] else "Onsite "
        print(f"     {label}  {row['percentage']}%  ({row['job_count']} jobs)")

    print("\n  👤 Experience Level Demand:")
    for row in dashboard["experience_demand"]:
        print(f"     {row['experience_level']:<12} {row['job_count']:>5} jobs")
    print("─" * 55)


def run_recommendation(db: DatabaseManager):
    """Example: skill gap recommendation for a sample candidate."""
    print("\n[Step 5] Running sample skill-gap recommendation ...")

    engine = RecommendationEngine(db)
    report = engine.analyse(
        candidate_skills   = ["python", "sql", "pandas", "flask"],
        experience_level   = "Mid-level",
    )

    CSVExporter().export_recommendations(report)

    print("\n  🎯 SKILL GAP RECOMMENDATIONS")
    print(f"  Your Skills: {', '.join(report['input']['candidate_skills'])}")
    print(f"  Level      : {report['input']['experience_level']}")
    print(f"\n  Skills to learn next (highest ROI):")
    for row in report["recommended_skills"][:5]:
        sal = f"  avg ${row['avg_salary']:,.0f}" if row["avg_salary"] else ""
        print(f"     ✦ {row['skill']:<20} ({row['demand_count']} jobs){sal}")

    sp = report["salary_potential"]
    if sp["current_avg_salary"]:
        print(f"\n  Salary Potential:")
        print(f"     Current  : ${sp['current_avg_salary']:,.0f}")
        print(f"     Potential: ${sp['potential_avg_salary']:,.0f}")
        print(f"     Uplift   : +${sp['estimated_uplift']:,.0f}")


# ── Entry Point ───────────────────────────────────────────────
def main():
    print(BANNER)

    db = DatabaseManager()
    try:
        db.connect()
        setup_database(db)
        collect_jobs(db)
        extract_and_store_skills(db)
        run_analytics_and_export(db)
        run_recommendation(db)
        print("\n✅ Pipeline complete. Reports saved in /reports/\n")
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        raise
    finally:
        db.disconnect()


if __name__ == "__main__":
    main()
