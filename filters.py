import re
import datetime as dt
import config

def _has(text, words):
    t = text.lower()
    return any(w in t for w in words)

_UNIT_MIN = {
    "second": 1/60, "sec": 1/60, "minute": 1, "min": 1, "hour": 60, "hr": 60,
    "day": 1440, "week": 10080, "month": 43200, "year": 525600
}
_REL = re.compile(r"(\d+|an?|one)\s*(second|sec|minute|min|hour|hr|day|week|month|year)s?\b", re.I)

def _parse_iso(s):
    s = (s or "").strip()
    if not s or re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):     # تاريخ من غير ساعة = مش دقيق
        return None
    try:
        clean = s.replace("Z", "+00:00")
        d = dt.datetime.fromisoformat(clean)
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d

def age_minutes(job, now=None):
    """عمر الوظيفة بالدقائق بدقة، أو None لو غير معروف."""
    now = now or dt.datetime.now(dt.timezone.utc)
    d = _parse_iso(job.posted_at)
    if d:
        return max(0.0, (now - d).total_seconds() / 60)
    raw = (job.posted_text or "").lower()
    if re.search(r"just now|moments? ago|few seconds|الآن", raw):
        return 0.0
    m = _REL.search(raw)
    if m:
        n = 1 if not m.group(1).isdigit() else int(m.group(1))
        unit = m.group(2).lower()
        return n * _UNIT_MIN.get(unit, 1440)
    return None

def is_fresh(job, max_minutes=None):
    """الوظيفة لازم تكون نازلة من أقل من 3 أيام كحد أقصى (72 ساعة)."""
    # 1. فحص التاريخ إن وُجد YYYY-MM-DD
    if job.posted_at and len(str(job.posted_at)) >= 10:
        try:
            job_date = dt.datetime.strptime(str(job.posted_at)[:10], "%Y-%m-%d").date()
            diff_days = (dt.date.today() - job_date).days
            if diff_days > 3:
                return False, f"too old ({diff_days} days ago)"
        except Exception:
            pass

    # 2. فحص النص إن وُجد (posted_text)
    raw = (job.posted_text or "").lower()
    if re.search(r"(\d+)\s*(?:month|year|week)s?\s*ago", raw):
        return False, f"too old ({raw})"
    m_days = re.search(r"(\d+)\s*days?\s*ago", raw)
    if m_days and int(m_days.group(1)) > 3:
        return False, f"too old ({raw})"

    limit = max_minutes or getattr(config, "MAX_AGE_MINUTES", 4320)
    # أقصى حد عام هو 3 أيام (4320 دقيقة)
    limit = min(limit, 4320)
    age = age_minutes(job)
    if age is not None:
        if age > limit:
            return False, f"too old ({int(age)} min)"
        return True, ""

    # إذا لم نتمكن من حساب الدقائق ولكن التاريخ لم يتجاوز 3 أيام
    if job.posted_at and len(str(job.posted_at)) >= 10:
        return True, ""
    if re.search(r"just now|today|yesterday|hours? ago|min|الآن|أمس", raw):
        return True, ""
    return False, "unknown or stale posting time"

def age_label(job):
    """صيغة مختصرة وأنيقة لعمر الوظيفة للرسالة والداشبورد."""
    age = age_minutes(job)
    if age is None:
        return job.posted_text or "recently"
    if age < 1:
        return "just now"
    if age < 90:
        return f"{int(age)} min ago"
    return f"{age/60:.1f} h ago"

# قائمة الشركات والوكالات المزعجة / الوهمية (مأخوذة من RTJobs-main)
BLOCKED_COMPANIES = [
    "hire feed", "telus digital", "jobs ai", "hired", "micro1", "crossing hurdles",
    "mindrift", "turing", "quik hire staffing", "alignerr", "outlier", "dataannotation",
    "remotasks", "appen", "oneforma", "welocalize", "invisible technologies", "cyberbacker"
]

def company_ok(job):
    """استبعاد الشركات الوهمية والمجمعات الإعلانية غير الموثوقة."""
    c = (job.company or "").lower().strip()
    if any(b in c for b in BLOCKED_COMPANIES):
        return False, f"blocked spam/agency company ({job.company})"
    return True, ""

def extract_salary(job):
    """استخراج الراتب بدقة إن وُجد (USD, EGP, EUR, GBP, SAR, AED)."""
    text = f"{job.title} {job.location} {job.description or ''}"
    # 1. USD: $1,000 - $3,000, $40k - $60k, $25/hr
    m_usd = re.search(r"(\$\s?[\d,]+(?:\.\d+)?\s*(?:k|K)?(?:\s*(?:-|to|–)\s*\$?\s*[\d,]+(?:\.\d+)?\s*(?:k|K)?)?(?:\s*(?:/|per)\s*(?:hr|hour|mo|month|yr|year))?)", text)
    if m_usd:
        return m_usd.group(1).strip()
    # 2. EGP: 15,000 - 25,000 EGP, ج.م
    m_egp = re.search(r"([\d,]+\s*(?:-|to|–)\s*[\d,]+\s*(?:EGP|LE|ج\.م|جنيه))", text, re.I)
    if m_egp:
        return m_egp.group(1).strip()
    # 3. EUR / GBP: €2,000 - €3,500, £30k
    m_eur = re.search(r"([€£]\s?[\d,]+(?:\s*(?:-|to|–)\s*[€£]?\s*[\d,]+)?(?:\s*(?:k|K))?(?:\s*(?:/|per)\s*(?:mo|yr))?)", text)
    if m_eur:
        return m_eur.group(1).strip()
    # 4. SAR / AED: 5,000 - 10,000 SAR/AED
    m_gulf = re.search(r"([\d,]+\s*(?:-|to|–)\s*[\d,]+\s*(?:SAR|AED|ريال|درهم))", text, re.I)
    if m_gulf:
        return m_gulf.group(1).strip()
    return ""

def extract_career_level(job):
    """تحديد المستوى الوظيفي بدقة من العنوان والوصف."""
    text = f"{job.title} {job.description or ''}".lower()
    if any(w in text for w in ["fresh graduate", "entry level", "entry-level", "junior", "jr.", "jr ", "مبتدئ", "حديث التخرج", "graduate program", "trainee"]):
        return "🌱 Junior / Entry Level"
    if any(w in text for w in ["mid-level", "mid level", "intermediate", "2-3 years"]):
        return "⚡ Mid-Level"
    if any(w in text for w in ["senior", "sr.", "lead", "principal"]):
        return "🔥 Senior"
    return "🌱 Entry Level"

def title_ok(job):
    t = " " + job.title.lower() + " "
    
    # 1. التحقق من وجود كلمات الوظيفة المستهدفة
    if not _has(t, config.TITLE_MUST_ANY):
        return False, "title not frontend/react/shopify/web"
        
    # 2. استبعاد المسميات الإدارية والعليا (Senior, Lead, Principal, etc.) ومجالات غير مرغوبة
    is_junior_explicit = any(j in t for j in ["junior", "jr.", "jr ", "entry level", "fresh", "مبتدئ"])
    
    effective_exclude = [
        ex for ex in config.TITLE_EXCLUDE 
        if not any(must == ex or must in ex for must in config.TITLE_MUST_ANY)
    ]
    if _has(t, effective_exclude):
        if not is_junior_explicit and not any(must in t for must in ["senior", "mid-level", "mid level"]):
            return False, "excluded title word"
            
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
    # 1. فحص حداثة الوظيفة
    fresh, why_stale = is_fresh(job)
    if not fresh:
        return False, why_stale

    # 2. فحص العنوان
    ok, why = title_ok(job)
    if not ok:
        return ok, why

    # 2b. استبعاد الشركات الوهمية والمجمعات الإعلانية
    ok, why = company_ok(job)
    if not ok:
        return ok, why

    text = f"{job.title}\n{job.description or ''}".lower()
    
    # 3. فحص الكلمات الإجبارية في الوصف إذا تم تحديدها
    if config.DESCRIPTION_MUST and job.description is not None and not _has(text, config.DESCRIPTION_MUST):
        return False, "required description keyword not mentioned"
        
    # 3b. لو العنوان عام (Software Engineer / Web Developer): لازم الوصف يذكر مهارة من مهاراتك
    if not _has(job.title.lower(), config.CORE_TITLE_WORDS):
        if job.description is None or not _has(text, config.CORE_SKILLS):
            return False, "generic title without react/frontend skills"

    # 4. استبعاد القيود الجغرافية الصارمة (مثل US Only لمقيم في مصر)
    if _has(text, config.BAD_PHRASES):
        return False, "location restricted"
        
    # 5. سنوات الخبرة
    y = min_years_required(text)
    if y is not None and y > config.MAX_YEARS_REQUIRED:
        return False, f"needs {y}+ years"
        
    return True, ""

def work_type(job):
    """Detect work arrangement: Remote, Hybrid, On-site."""
    title = (job.title or "").lower()
    loc = (job.location or "").lower()
    desc = (job.description or "").lower()
    combined = f"{title} {loc} {desc}"

    # إذا كان العنوان يقول صراحة onsite أو on-site
    if re.search(r"\b(onsite|on-site|in-office)\b", title):
        return "On-site"

    is_remote = False
    if "remote" in title or "remote" in loc:
        is_remote = True
    elif "remote" in desc and not re.search(r"\b(no\s+remote|not\s+remote|non-remote)\b", desc):
        is_remote = True
    elif getattr(job, "remote_search", False) and not re.search(r"\b(onsite|on-site|in-office)\b", combined):
        is_remote = True

    is_hybrid = "hybrid" in combined
    is_onsite = bool(re.search(r"\b(on-?site|in-office)\b", combined))

    if is_remote and not is_onsite and not is_hybrid:
        return "Remote"
    if is_hybrid:
        return "Hybrid"
    if is_remote and is_onsite:
        return "Remote / On-site"
    return "On-site"

def extract_country(job):
    """Extract country name from job location string."""
    loc = (job.location or "").lower()
    
    country_map = {
        "egypt": "🇪🇬 Egypt", "cairo": "🇪🇬 Egypt", "giza": "🇪🇬 Egypt",
        "alexandria": "🇪🇬 Egypt", "maadi": "🇪🇬 Egypt", "nasr city": "🇪🇬 Egypt",
        "6th of october": "🇪🇬 Egypt", "new cairo": "🇪🇬 Egypt", "smart village": "🇪🇬 Egypt",
        "mansoura": "🇪🇬 Egypt", "مصر": "🇪🇬 Egypt", "القاهرة": "🇪🇬 Egypt",
        "philippines": "🇵🇭 Philippines", "manila": "🇵🇭 Philippines", "pasig": "🇵🇭 Philippines",
        "united states": "🇺🇸 USA", "usa": "🇺🇸 USA", "new york": "🇺🇸 USA",
        "san francisco": "🇺🇸 USA", "los angeles": "🇺🇸 USA", "chicago": "🇺🇸 USA",
        "boston": "🇺🇸 USA", "seattle": "🇺🇸 USA", "austin": "🇺🇸 USA",
        "united kingdom": "🇬🇧 UK", "london": "🇬🇧 UK", "manchester": "🇬🇧 UK",
        "germany": "🇩🇪 Germany", "berlin": "🇩🇪 Germany", "munich": "🇩🇪 Germany",
        "france": "🇫🇷 France", "paris": "🇫🇷 France", "lyon": "🇫🇷 France",
        "canada": "🇨🇦 Canada", "toronto": "🇨🇦 Canada", "vancouver": "🇨🇦 Canada",
        "netherlands": "🇳🇱 Netherlands", "amsterdam": "🇳🇱 Netherlands",
        "india": "🇮🇳 India", "bangalore": "🇮🇳 India", "bengaluru": "🇮🇳 India", "mumbai": "🇮🇳 India", "pune": "🇮🇳 India",
        "uae": "🇦🇪 UAE", "dubai": "🇦🇪 UAE", "abu dhabi": "🇦🇪 UAE",
        "saudi": "🇸🇦 Saudi Arabia", "riyadh": "🇸🇦 Saudi Arabia", "jeddah": "🇸🇦 Saudi Arabia",
        "qatar": "🇶🇦 Qatar", "doha": "🇶🇦 Qatar",
        "jordan": "🇯🇴 Jordan", "amman": "🇯🇴 Jordan",
        "spain": "🇪🇸 Spain", "barcelona": "🇪🇸 Spain", "madrid": "🇪🇸 Spain",
        "portugal": "🇵🇹 Portugal", "lisbon": "🇵🇹 Portugal",
        "turkey": "🇹🇷 Turkey", "istanbul": "🇹🇷 Turkey",
        "singapore": "🇸🇬 Singapore", "australia": "🇦🇺 Australia",
        "ireland": "🇮🇪 Ireland", "dublin": "🇮🇪 Ireland",
        "poland": "🇵🇱 Poland", "warsaw": "🇵🇱 Poland",
        "sweden": "🇸🇪 Sweden", "stockholm": "🇸🇪 Sweden",
        "italy": "🇮🇹 Italy", "milan": "🇮🇹 Italy", "rome": "🇮🇹 Italy",
    }
    
    for key, country in country_map.items():
        if key in loc:
            return country
    
    # Remote / worldwide (فقط إذا لم يكن مذكور دولة محددة)
    remote_words = ["worldwide", "anywhere", "global", "remote", "emea", "mena"]
    if any(w in loc for w in remote_words) or not loc.strip():
        return "🌐 Worldwide"
    
    raw = (job.location or "").strip()
    return raw[:30] if raw else "🌐 Worldwide"

def is_egypt_loc(text):
    t = (text or "").lower()
    egypt_words = [
        "egypt", "cairo", "giza", "alexandria", "mansoura", "6th of october", "new cairo",
        "maadi", "nasr city", "smart village", "tanta", "asyut", "suez", "ismailia",
        "مصر", "القاهرة", "الجيزة", "الإسكندرية", "المعادي", "مدينة نصر", "أكتوبر"
    ]
    return any(w in t for w in egypt_words)

def egypt_or_remote(job):
    loc = (job.location or "").lower()
    desc = (job.description or "").lower()
    title = (job.title or "").lower()
    country = (getattr(job, "country", "") or "").lower()
    combined = f"{title}\n{loc}\n{country}\n{desc}"

    # 1. إذا كانت الوظيفة في مصر: مقبولة بكل أنواع العمل (أونسايت، هايبرد، ريموت)
    if is_egypt_loc(loc) or is_egypt_loc(country) or "based in egypt" in combined or "cairo, egypt" in combined:
        return True

    # 2. إذا كانت الوظيفة خارج مصر:
    # شرط صارم ومطلق من المستخدمة: خارج مصر = REMOTE 100% فقط! أي On-site أو Hybrid خارج مصر مرفوض فوراً!
    if re.search(r"\b(onsite|on-site|in-office|office based|relocate|relocation)\b", title):
        return False

    wt = (getattr(job, "work_type", "") or "").lower()
    if not wt:
        wt = work_type(job).lower()

    if "on-site" in wt or "onsite" in wt or "in-office" in wt:
        return False
    if "hybrid" in wt:
        return False
    if "remote" not in wt:
        return False

    # قيود الإقامة الصارمة التي تمنع المقيمين في مصر
    country_locks = [
        "us only", "u.s. only", "united states only", "must reside in the us", "must be based in the us",
        "us citizen", "u.s. citizen", "green card", "security clearance", "authorized to work in the united states",
        "uk only", "must be based in the uk", "right to work in the uk", "uk citizen",
        "remote-based in portugal", "based in portugal", "living in portugal",
        "canada only", "must be based in canada", "latam only", "germany only", "eu citizen only"
    ]
    if any(lock in combined for lock in country_locks):
        return False

    # التحقق من وجود مؤشر واضح على العمل عن بُعد المفتوح
    remote_ok = ["worldwide", "anywhere", "global", "emea", "africa", "middle east", "mena", "remote", "work from anywhere", "100% remote"]
    if any(w in combined for w in remote_ok) or getattr(job, "remote_search", False):
        return True

    return False

def calculate_fit(job):
    """
    Computes fit score (0-100), verdict band, strengths, gaps, and CV suggestions
    tailored to Arwa Ahmed's persona and projects.
    """
    title = (job.title or "").lower()
    desc = (job.description or "").lower()
    text = f"{title}\n{desc}"

    # 1. Technical Score (0 - 100)
    primary_skills = ["react", "next.js", "nextjs", "node.js", "nodejs", "typescript", "javascript", "tailwind", "rest api", "restful"]
    secondary_skills = ["express", "postgresql", "mongodb", "mysql", "prisma", "redux", "zustand", "git", "socket.io", "nestjs"]
    
    primary_hits = sum(1 for s in primary_skills if s in text)
    secondary_hits = sum(1 for s in secondary_skills if s in text)
    
    tech_score = min(100, int((primary_hits * 18) + (secondary_hits * 10) + 10))

    # 2. Experience / Seniority Score (0 - 100)
    exp_score = 80
    if any(w in title for w in ["junior", "jr", "entry level", "fresh", "graduate", "associate", "trainee"]):
        exp_score = 95
    elif any(w in title for w in ["senior", "lead", "principal", "staff"]):
        exp_score = 25
    elif any(w in desc for w in ["0-1 years", "0-2 years", "1-2 years", "1+ year"]):
        exp_score = 90
    elif any(w in desc for w in ["5+ years", "6+ years", "7+ years"]):
        exp_score = 30

    # 3. Behavioral / Work Environment (0 - 100)
    behav_score = 85
    if "remote" in text or "hybrid" in text or "flexible" in text:
        behav_score += 10

    # Weighted Overall Score
    overall = int((tech_score * 0.5) + (exp_score * 0.35) + (behav_score * 0.15))
    overall = max(0, min(100, overall))

    # Verdict Band
    if overall >= 85:
        verdict = "Strong Fit"
    elif overall >= 70:
        verdict = "Good Fit"
    elif overall >= 50:
        verdict = "Moderate Fit"
    else:
        verdict = "Low Fit"

    # Strengths / Gaps
    strengths = [s.title() for s in primary_skills + secondary_skills if s in text][:5]
    if not strengths:
        strengths = ["Frontend Foundations", "Responsive Design"]

    missing_candidates = ["TypeScript", "Next.js", "Tailwind CSS", "Redux Toolkit", "GraphQL", "Docker"]
    gaps = [m for m in missing_candidates if m.lower() not in text][:3]

    cv_suggs = [
        f"Highlight hands-on projects with {strengths[0]}" if strengths else "Feature your recent React portfolio",
        f"Address requirement for {gaps[0]} by showcasing related skills" if gaps else "Emphasize clean code and git workflows"
    ]

    return overall, verdict, strengths, gaps, cv_suggs
