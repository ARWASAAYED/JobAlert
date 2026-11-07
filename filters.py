import re
import config

def _has(text, words):
    t = text.lower()
    return any(w in t for w in words)

def title_ok(job):
    t = " " + job.title.lower() + " "
    if not _has(t, config.TITLE_MUST_ANY):
        return False, "title not frontend/react"
    if _has(t, config.TITLE_EXCLUDE):
        return False, "excluded title word"
    if _has(t, config.OTHER_FRAMEWORKS) and not any(k in t for k in ["react", "frontend", "front end", "shopify"]):
        return False, "other framework"
    return True, ""

def min_years_required(text):
    """أقل رقم سنين خبرة مذكور جنب كلمة experience. None لو مفيش."""
    found = []
    for m in re.finditer(r"(\d+)\s*\+?\s*(?:-|–|to)?\s*(\d+)?\s*\+?\s*(?:years?|yrs?)", text, re.I):
        window = text[max(0, m.start() - 80): m.end() + 80].lower()
        if "experience" in window or "خبرة" in window:
            found.append(int(m.group(1)))
    return min(found) if found else None

def full_ok(job):
    ok, why = title_ok(job)
    if not ok:
        return ok, why
    text = f"{job.title}\n{job.description or ''}".lower()
    if config.DESCRIPTION_MUST and job.description is not None and not _has(text, config.DESCRIPTION_MUST):
        return False, "required description keyword not mentioned"
    if _has(text, config.BAD_PHRASES):
        return False, "location restricted"
    y = min_years_required(text)
    if y is not None and y > config.MAX_YEARS_REQUIRED:
        return False, f"needs {y}+ years"
    return True, ""

def work_type(job):
    t = f"{job.title} {job.location} {job.description or ''}".lower()
    kinds = []
    if "remote" in t or job.remote_search: kinds.append("Remote")
    if "hybrid" in t: kinds.append("Hybrid")
    if re.search(r"on-?\s?site", t): kinds.append("On-site")
    return " / ".join(kinds) or "غير محدد"

def egypt_or_remote(job):
    loc = job.location.lower()
    egypt = ["egypt", "cairo", "giza", "alexandria", "mansoura", "6th of october", "new cairo",
             "maadi", "nasr city", "smart village", "مصر", "القاهرة", "الجيزة", "الإسكندرية"]
    remote_ok = ["worldwide", "anywhere", "global", "emea", "africa", "middle east", "mena", "remote"]
    if job.remote_search or loc.strip() == "":
        return True
    return _has(loc, egypt + remote_ok)
