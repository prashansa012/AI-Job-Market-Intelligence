# ============================================================
#  collectors/muse_collector.py  —  The Muse API Collector
# ============================================================

import requests
from datetime import date, datetime
from config.settings import MUSE_API_KEY, MUSE_PAGE_SIZE


class MuseCollector:
    """Fetches job postings from The Muse API."""

    BASE_URL = "https://www.themuse.com/api/public/jobs"

    def collect(self, pages: int = 3) -> list[dict]:
        print("  [TheMuse] Fetching jobs ...")
        all_jobs = []
        for page in range(pages):
            try:
                jobs = self._fetch_page(page)
                if not jobs:
                    break
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"  [TheMuse] Error on page {page}: {e}")
                break
        print(f"  [TheMuse] → {len(all_jobs)} jobs collected")
        return all_jobs

    def _fetch_page(self, page: int) -> list[dict]:
        params = {
            "api_key":  MUSE_API_KEY,
            "page":     page,
            "descending": "true",
        }
        resp = requests.get(self.BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return [self._normalise(r) for r in results]

    def _normalise(self, r: dict) -> dict:
        # Location
        locations = r.get("locations", [])
        location_str = locations[0].get("name", "") if locations else "Unknown"
        city  = location_str.split(",")[0].strip() if "," in location_str else location_str
        is_remote = "remote" in location_str.lower() or "flexible" in location_str.lower()

        # Date
        pub = r.get("publication_date", "")
        try:
            posted_date = datetime.fromisoformat(pub[:10]).date() if pub else date.today()
        except Exception:
            posted_date = date.today()

        # Experience from categories
        categories = [c.get("name", "") for c in r.get("categories", [])]
        exp_level  = self._parse_experience(r.get("name", ""), categories)

        return {
            "job_id":           f"muse_{r.get('id', '')}",
            "title":            r.get("name", ""),
            "company":          r.get("company", {}).get("name", ""),
            "location":         location_str,
            "city":             city,
            "country":          "US",
            "salary_min":       None,
            "salary_max":       None,
            "salary_avg":       None,
            "description":      r.get("contents", ""),
            "job_type":         r.get("type", "full_time"),
            "is_remote":        is_remote,
            "experience_level": exp_level,
            "source":           "themuse",
            "url":              r.get("refs", {}).get("landing_page", ""),
            "posted_date":      posted_date,
        }

    @staticmethod
    def _parse_experience(title: str, categories: list[str]) -> str:
        combined = (title + " ".join(categories)).lower()
        if any(w in combined for w in ["senior", "lead", "principal", "staff"]):
            return "Senior"
        if any(w in combined for w in ["entry", "junior", "associate", "intern"]):
            return "Junior"
        if any(w in combined for w in ["manager", "director", "vp", "head"]):
            return "Manager"
        return "Mid-level"
