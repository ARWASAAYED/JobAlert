import re
import datetime as dt
import config

def _has(text, words):
    t = text.lower()
    return any(w in t for w in words)

def is_fresh(job, max_hours=48):
    """
    يتأكد أن الوظيفة حديثة وليست من أسبوعين أو شهور سابقة.
    يرفض الوظائف التي كُتب عليها (2 weeks ago, 1 month ago, إلخ).
    """
    raw = (job.posted_text or "").lower().strip()
    
    # استبعاد صريح للوظائف القديمة جداً
    stale_indicators = ["week", "month", "year", "أسبوع", "شهر", "سنة", "14d", "15d", "20d", "30d"]
    if any(si in raw for si in stale_indicators):
        # إلا لو مكتوب "1 week" ولكن منشور خلال آخر 48 ساعة فعلياً
        return False, f"too old ({raw})"

    # فحص تاريخ النشر الفعلي إذا كان متوفراً
    if job.posted_at:
        try:
            # الصيغة: YYYY-MM-DD HH:MM
            job_dt = dt.datetime.strptime(job.posted_at[:16], "%Y-%m-%d %H:%M")
            diff = (dt.datetime.now() - job_dt).total_seconds() / 3600
            if diff > max_hours:
                return False, f"older than {max_hours}h ({int(diff)}h ago)"
        except Exception:
            pass

    return True, ""

def title_ok(job):
    t = " " + job.title.lower() + " "
    
    # 1. التحقق من وجود كلمات الوظيفة المستهدفة
    if not _has(t, config.TITLE_MUST_ANY):
        return False, "title not frontend/react/shopify/web"
        
    # 2. استبعاد المسميات الإدارية والعليا (Senior, Lead, Principal, etc.)
    # استثناء: إذا كان العنوان فيه junior frontend / junior react نسمح به حتى لو ذكر كلمات أخرى
    is_junior_explicit = any(j in t for j in ["junior", "jr.", "jr ", "entry level", "fresh", "مبتدئ"])
    
    if _has(t, config.TITLE_EXCLUDE):
        if not is_junior_explicit:
            return False, "excluded title word (senior/lead)"
            
    # 3. إطارات العمل الأخرى غير المستهدفة
    if _has(t, config.OTHER_FRAMEWORKS) and not any(k in t for k in ["react", "frontend", "front end", "shopify", "next"]):
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
    # 1. فحص حداثة الوظيفة (طرد الوظائف القديمة من أسبوعين وشهور)
    fresh, why_stale = is_fresh(job, max_hours=48)
    if not fresh:
        return False, why_stale

    # 2. فحص العنوان
    ok, why = title_ok(job)
    if not ok:
        return ok, why

    text = f"{job.title}\n{job.description or ''}".lower()
    
    # 3. فحص الكلمات الإجبارية في الوصف إذا تم تحديدها
    if config.DESCRIPTION_MUST and job.description is not None and not _has(text, config.DESCRIPTION_MUST):
        return False, "required description keyword not mentioned"
        
    # 4. استبعاد القيود الجغرافية الصارمة (مثل US Only لمقيم في مصر)
    if _has(text, config.BAD_PHRASES):
        return False, "location restricted"
        
    # 5. سنوات الخبرة
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
