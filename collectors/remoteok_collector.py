# ============================================================
#  collectors/remoteok_collector.py  —  RemoteOK API Collector
# ============================================================

import requests
from datetime import date, datetime


class RemoteOKCollector:
    """Fetches remote job postings from the free RemoteOK API."""

    API_URL = "https://remoteok.com/api"

    def collect(self) -> list[dict]:
        print("  [RemoteOK] Fetching remote jobs ...")
        try:
            headers = {"User-Agent": "JobMarketIntelligence/1.0"}
            resp    = requests.get(self.API_URL, headers=headers, timeout=20)
            resp.raise_for_status()
            raw = resp.json()
            # First element is a legal notice dict — skip it
            jobs = [r for r in raw if isinstance(r, dict) and r.get("id")]
            normalised = [self._normalise(j) for j in jobs]
            print(f"  [RemoteOK] → {len(normalised)} jobs collected")
            return normalised
        except Exception as e:
            print(f"  [RemoteOK] Error: {e}")
            return []

    def _normalise(self, r: dict) -> dict:
        salary_min = self._safe_float(r.get("salary_min"))
        salary_max = self._safe_float(r.get("salary_max"))
        salary_avg = None
        if salary_min and salary_max:
            salary_avg = (salary_min + salary_max) / 2

        epoch = r.get("epoch")
        try:
            posted_date = datetime.fromtimestamp(epoch).date() if epoch else date.today()
        except Exception:
            posted_date = date.today()

        return {
            "job_id":           f"rok_{r.get('id', '')}",
            "title":            r.get("position", ""),
            "company":          r.get("company", ""),
            "location":         "Remote / Worldwide",
            "city":             None,
            "country":          "REMOTE",
            "salary_min":       salary_min,
            "salary_max":       salary_max,
            "salary_avg":       salary_avg,
            "description":      r.get("description", ""),
            "job_type":         "remote",
            "is_remote":        True,
            "experience_level": self._parse_experience(r.get("position", "")),
            "source":           "remoteok",
            "url":              r.get("url", ""),
            "posted_date":      posted_date,
        }

    @staticmethod
    def _safe_float(val) -> float | None:
        try:
            return float(val) if val else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_experience(title: str) -> str:
        title = title.lower()
        if any(w in title for w in ["senior", "lead", "principal", "staff", "sr"]):
            return "Senior"
        if any(w in title for w in ["junior", "jr", "entry", "intern", "fresher", "trainee"]):
            return "Junior"
        if any(w in title for w in ["manager", "director", "head", "vp"]):
            return "Manager"
        return "Mid-level"
