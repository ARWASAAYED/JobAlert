"""
Application Tracker & Deadline Sweeper.
Tracks jobs you've applied to, stages (identified, applied, screening, interview, offer, rejected),
and sweeps upcoming deadlines.
"""

import os
import csv
from datetime import datetime, date

DEFAULT_TRACKER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tracker.csv")

FIELDS = ["job_key", "title", "company", "url", "status", "applied_date", "deadline", "fit_score", "notes"]

def init_tracker(path: str = DEFAULT_TRACKER_PATH):
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()

def load_tracker(path: str = DEFAULT_TRACKER_PATH) -> list[dict]:
    init_tracker(path)
    rows = []
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def save_tracker(rows: list[dict], path: str = DEFAULT_TRACKER_PATH):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

def track_job(job_key: str, title: str, company: str, url: str, status: str = "identified", 
              applied_date: str = "", deadline: str = "", fit_score: int = 0, notes: str = "",
              path: str = DEFAULT_TRACKER_PATH):
    init_tracker(path)
    rows = load_tracker(path)
    for r in rows:
        if r["job_key"] == job_key:
            r["status"] = status
            if applied_date: r["applied_date"] = applied_date
            if deadline: r["deadline"] = deadline
            if fit_score: r["fit_score"] = str(fit_score)
            if notes: r["notes"] = notes
            save_tracker(rows, path)
            return r

    new_row = {
        "job_key": job_key,
        "title": title,
        "company": company,
        "url": url,
        "status": status,
        "applied_date": applied_date or (datetime.now().strftime("%Y-%m-%d") if status == "applied" else ""),
        "deadline": deadline,
        "fit_score": str(fit_score),
        "notes": notes
    }
    rows.append(new_row)
    save_tracker(rows, path)
    return new_row

def deadline_sweep(path: str = DEFAULT_TRACKER_PATH) -> dict:
    """
    Finds jobs whose application deadline is within 7 days, or already expired.
    """
    rows = load_tracker(path)
    today = date.today()
    closing_soon = []
    expired = []

    for r in rows:
        dl_str = (r.get("deadline") or "").strip()
        if not dl_str:
            continue
        try:
            dl = datetime.strptime(dl_str[:10], "%Y-%m-%d").date()
            diff = (dl - today).days
            if diff < 0:
                expired.append({**r, "days_left": diff})
            elif diff <= 7:
                closing_soon.append({**r, "days_left": diff})
        except Exception:
            pass

    return {
        "closing_soon": closing_soon,
        "expired": expired
    }

