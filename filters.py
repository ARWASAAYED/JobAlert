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
    """Detect work arrangement: Remote, Hybrid, On-site."""
    t = f"{job.title} {job.location} {job.description or ''}".lower()
    kinds = []
    if "remote" in t or job.remote_search: kinds.append("Remote")
    if "hybrid" in t: kinds.append("Hybrid")
    if re.search(r"on-?\s?site", t): kinds.append("On-site")
    return " / ".join(kinds) or "On-site"

def extract_country(job):
    """Extract country name from job location string."""
    loc = (job.location or "").lower()
    
    country_map = {
        "egypt": "🇪🇬 Egypt", "cairo": "🇪🇬 Egypt", "giza": "🇪🇬 Egypt",
        "alexandria": "🇪🇬 Egypt", "maadi": "🇪🇬 Egypt", "nasr city": "🇪🇬 Egypt",
        "6th of october": "🇪🇬 Egypt", "new cairo": "🇪🇬 Egypt", "smart village": "🇪🇬 Egypt",
        "mansoura": "🇪🇬 Egypt", "مصر": "🇪🇬 Egypt", "القاهرة": "🇪🇬 Egypt",
        "united states": "🇺🇸 USA", "usa": "🇺🇸 USA", "new york": "🇺🇸 USA",
        "san francisco": "🇺🇸 USA", "los angeles": "🇺🇸 USA", "chicago": "🇺🇸 USA",
        "boston": "🇺🇸 USA", "seattle": "🇺🇸 USA", "austin": "🇺🇸 USA",
        "united kingdom": "🇬🇧 UK", "london": "🇬🇧 UK", "manchester": "🇬🇧 UK",
        "germany": "🇩🇪 Germany", "berlin": "🇩🇪 Germany", "munich": "🇩🇪 Germany",
        "france": "🇫🇷 France", "paris": "🇫🇷 France",
        "canada": "🇨🇦 Canada", "toronto": "🇨🇦 Canada", "vancouver": "🇨🇦 Canada",
        "netherlands": "🇳🇱 Netherlands", "amsterdam": "🇳🇱 Netherlands",
        "india": "🇮🇳 India", "bangalore": "🇮🇳 India", "mumbai": "🇮🇳 India",
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
    }
    
    for key, country in country_map.items():
        if key in loc:
            return country
    
    # Remote / worldwide
    remote_words = ["worldwide", "anywhere", "global", "remote", "emea", "mena"]
    if any(w in loc for w in remote_words) or job.remote_search:
        return "🌐 Worldwide"
    
    # If we can't detect, return the raw location trimmed
    raw = (job.location or "").strip()
    return raw[:30] if raw else "🌍 Unknown"

def egypt_or_remote(job):
    loc = (job.location or "").lower()
    desc = (job.description or "").lower()
    title = (job.title or "").lower()
    combined = f"{title}\n{loc}\n{desc}"

    # 1. Egypt is always PASS (Candidate's home place)
    egypt = [
        "egypt", "cairo", "giza", "alexandria", "mansoura", "6th of october", "new cairo",
        "maadi", "nasr city", "smart village", "مصر", "القاهرة", "الجيزة", "الإسكندرية"
    ]
    if _has(loc, egypt) or any(e in combined for e in ["based in egypt", "cairo, egypt"]):
        return True

    # 2. Check for explicit country locks that prevent candidate in Egypt from working remotely
    country_locks = [
        "us only", "u.s. only", "united states only", "must reside in the us", "must be based in the us",
        "us citizen", "u.s. citizen", "green card", "security clearance", "authorized to work in the united states",
        "uk only", "must be based in the uk", "right to work in the uk", "uk citizen",
        "remote-based in portugal", "based in portugal", "living in portugal",
        "canada only", "must be based in canada", "latam only", "germany only", "eu citizen only"
    ]
    if any(lock in combined for lock in country_locks):
        return False

    # 3. Valid remote scopes (EMEA, Worldwide, Global, or general remote without exclusive country lock)
    remote_ok = ["worldwide", "anywhere", "global", "emea", "africa", "middle east", "mena", "remote"]
    if job.remote_search or loc.strip() == "":
        return True
    return _has(loc, remote_ok)


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
    if "ai" in text or "open source" in text or "opensource" in text:
        behav_score += 10
    behav_score = min(100, behav_score)

    # 4. Career Alignment (0 - 100)
    career_score = 75
    if any(w in title for w in ["full stack", "fullstack", "full-stack"]):
        career_score = 95
    elif any(w in title for w in ["frontend", "front-end", "web developer"]):
        career_score = 90
    elif "react" in title:
        career_score = 92

    # Weighted Overall Score (30% Tech, 25% Exp, 15% Behav, 30% Career)
    final_score = int((tech_score * 0.30) + (exp_score * 0.25) + (behav_score * 0.15) + (career_score * 0.30))
    final_score = max(0, min(100, final_score))

    if final_score >= 85:
        verdict = "Strong Fit"
    elif final_score >= 70:
        verdict = "Good Fit"
    elif final_score >= 50:
        verdict = "Moderate Fit"
    else:
        verdict = "Weak Fit"

    # Strengths
    strengths = []
    matched_stack = [s for s in ["React", "TypeScript", "Next.js", "Node.js", "Tailwind CSS", "PostgreSQL", "MongoDB", "NestJS", "RESTful APIs"] if s.lower() in text]
    if matched_stack:
        strengths.append(f"Strong stack alignment on {', '.join(matched_stack[:4])}.")
    if any(w in text for w in ["ai", "copilot", "cursor", "llm"]):
        strengths.append("Values AI-assisted workflows which aligns directly with your tooling.")
    if any(w in text for w in ["open source", "opensource"]):
        strengths.append("Values open source contributions, matching your DEY HireReady NTI experience.")
    if any(w in title for w in ["junior", "entry", "fresh"]):
        strengths.append("Ideal seniority fit explicitly targeting junior / entry-level developers.")
    if not strengths:
        strengths.append("Matches fundamental full-stack web development principles.")

    # Gaps
    gaps = []
    for g in ["Docker", "Kubernetes", "GraphQL", "AWS", "CI/CD", "Redis", "Microservices"]:
        if g.lower() in text:
            gaps.append(f"Mentions {g}.")
            if len(gaps) >= 2:
                break
    if not gaps:
        gaps.append("Standard competitive applicant pool.")

    # Tailored CV suggestions
    cv_suggestions = []
    if any(w in text for w in ["healthcare", "health", "hospital", "clinic", "doctor"]):
        cv_suggestions.append("Lead with your MediCare project (role-based hospital platform with doctor scheduling and appointments).")
    elif any(w in text for w in ["school", "education", "student", "learning", "lms"]):
        cv_suggestions.append("Lead with your School Management Dashboard (4 role-based portals with Next.js, Prisma, and PostgreSQL).")
    elif any(w in text for w in ["social", "chat", "messaging", "real-time", "socket"]):
        cv_suggestions.append("Lead with your BusinessNet platform (real-time messaging with Socket.io, Node.js, and MongoDB).")
    elif any(w in text for w in ["ecommerce", "e-commerce", "shop", "store", "product"]):
        cv_suggestions.append("Lead with ShopEase or EventChamp (product filtering, REST APIs, Redux Toolkit).")
    else:
        cv_suggestions.append("Highlight your School Management Dashboard (Next.js, TypeScript, PostgreSQL) as your primary full-stack architecture showcase.")

    if any(w in text for w in ["performance", "optimization", "lighthouse", "fast"]):
        cv_suggestions.append("Emphasize your Lighthouse performance score (>90) and reducing unnecessary API requests by 40%.")
    elif any(w in text for w in ["open source", "community"]):
        cv_suggestions.append("Feature your DEY HireReady NTI experience as Open-Source Applications Developer.")
    else:
        cv_suggestions.append("Surface your experience designing 25+ RESTful APIs with response times under 250ms.")

    return final_score, verdict, strengths[:3], gaps[:3], cv_suggestions[:2]
