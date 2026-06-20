# ============================================================
#  collectors/adzuna_collector.py  —  Adzuna API Collector
# ============================================================

import requests
from datetime import datetime, date
from config.settings import (
    ADZUNA_APP_ID, ADZUNA_API_KEY,
    ADZUNA_COUNTRY, ADZUNA_RESULTS_PAGE, MAX_PAGES_PER_RUN,
)


class AdzunaCollector:
    """Fetches job postings from the Adzuna API."""

    BASE_URL = "https://api.adzuna.com/v1/api/jobs"

    def __init__(self):
        self.app_id  = ADZUNA_APP_ID
        self.api_key = ADZUNA_API_KEY
        self.country = ADZUNA_COUNTRY

    # ── Public ────────────────────────────────────────────────
    def collect(self, keywords: list[str] = None) -> list[dict]:
        """
        Collect jobs for a list of keyword queries.
        Returns a flat list of normalised job dicts.
        """
        keywords = keywords or ["python developer", "data scientist",
                                "software engineer", "machine learning"]
        all_jobs = []
        for kw in keywords:
            print(f"  [Adzuna] Searching: '{kw}' ...")
            jobs = self._fetch_keyword(kw)
            print(f"           → {len(jobs)} jobs collected")
            all_jobs.extend(jobs)
        # deduplicate by job_id
        seen, unique = set(), []
        for j in all_jobs:
            if j["job_id"] not in seen:
                seen.add(j["job_id"])
                unique.append(j)
        return unique

    # ── Private ───────────────────────────────────────────────
    def _fetch_keyword(self, keyword: str) -> list[dict]:
        jobs = []
        for page in range(1, MAX_PAGES_PER_RUN + 1):
            try:
                raw = self._api_call(keyword, page)
                if not raw:
                    break
                jobs.extend(self._normalise(raw))
            except Exception as e:
                print(f"  [Adzuna] Error on page {page}: {e}")
                break
        return jobs

    def _api_call(self, keyword: str, page: int) -> list:
        url    = f"{self.BASE_URL}/{self.country}/search/{page}"
        params = {
            "app_id":          self.app_id,
            "app_key":         self.api_key,
            "results_per_page": ADZUNA_RESULTS_PAGE,
            "what":            keyword,
            "content-type":    "application/json",
        }
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json().get("results", [])

    def _normalise(self, raw_jobs: list) -> list[dict]:
        """Map Adzuna fields → our schema."""
        normalised = []
        for r in raw_jobs:
            salary_min = r.get("salary_min")
            salary_max = r.get("salary_max")
            salary_avg = None
            if salary_min and salary_max:
                salary_avg = (float(salary_min) + float(salary_max)) / 2

            location   = r.get("location", {})
            area        = location.get("area", [])
            city        = area[-1] if area else None

            posted_raw = r.get("created")
            try:
                posted_date = datetime.fromisoformat(
                    posted_raw.replace("Z", "+00:00")
                ).date()
            except Exception:
                posted_date = date.today()

            normalised.append({
                "job_id":           str(r.get("id", "")),
                "title":            r.get("title", ""),
                "company":          r.get("company", {}).get("display_name", ""),
                "location":         location.get("display_name", ""),
                "city":             city,
                "country":          self.country.upper(),
                "salary_min":       float(salary_min) if salary_min else None,
                "salary_max":       float(salary_max) if salary_max else None,
                "salary_avg":       salary_avg,
                "description":      r.get("description", ""),
                "job_type":         r.get("contract_time", "full_time"),
                "is_remote":        "remote" in r.get("description", "").lower(),
                "experience_level": self._parse_experience(r.get("title", "")),
                "source":           "adzuna",
                "url":              r.get("redirect_url", ""),
                "posted_date":      posted_date,
            })
        return normalised

    @staticmethod
    def _parse_experience(title: str) -> str:
        title = title.lower()
        if any(w in title for w in ["senior", "sr.", "lead", "principal", "staff"]):
            return "Senior"
        if any(w in title for w in ["junior", "jr.", "entry", "fresher", "trainee", "intern"]):
            return "Junior"
        if any(w in title for w in ["manager", "director", "head", "vp", "chief"]):
            return "Manager"
        return "Mid-level"
