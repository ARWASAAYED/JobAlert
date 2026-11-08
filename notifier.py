import html, requests
from urllib.parse import quote
import config
from filters import work_type, extract_country

API = "https://api.telegram.org/bot{}/{}"

def enabled():
    return bool(config.TELEGRAM_TOKEN and config.TELEGRAM_CHAT_ID)


def _post(method, **payload):
    r = requests.post(API.format(config.TELEGRAM_TOKEN, method), json=payload, timeout=20)
    if r.status_code == 429:
        import time; time.sleep(r.json().get("parameters", {}).get("retry_after", 5))
        r = requests.post(API.format(config.TELEGRAM_TOKEN, method), json=payload, timeout=20)
    r.raise_for_status()
    return r.json()

def send_text(text):
    _post("sendMessage", chat_id=config.TELEGRAM_CHAT_ID, text=text, parse_mode="HTML",
          disable_web_page_preview=True)

def send_job(job):
    e = html.escape
    
    # Detect work type and country
    wt = getattr(job, "work_type", "") or work_type(job)
    country = getattr(job, "country", "") or extract_country(job)
    
    # Select appropriate flag from country
    if "🇪🇬" in country:
        flag = "🇪🇬"
    elif "🌐" in country:
        flag = "🌐"
    else:
        parts = country.split(" ")
        flag = parts[0] if parts and len(parts[0]) <= 4 else "🌍"

    title = e(job.title)
    comp = e(job.company or "Company")
    loc = e(job.location or "Egypt")
    posted = e(job.posted_at or job.posted_text or "Just now")
    url = job.url

    # Work type badge (Remote / Hybrid / On-site)
    wt_lower = wt.lower()
    if "remote" in wt_lower:
        wt_badge = "🏠 Remote"
    elif "hybrid" in wt_lower:
        wt_badge = "🔄 Hybrid"
    else:
        wt_badge = "🏢 On-site"

    # Score badge
    score_badge = ""
    score = getattr(job, "score", 0)
    if score >= 85:
        score_badge = f"🏆 <b>Strong Fit ({score}%)</b>\n"
    elif score >= 70:
        score_badge = f"🥈 <b>Good Fit ({score}%)</b>\n"
    elif score >= 50:
        score_badge = f"🥉 <b>Moderate Fit ({score}%)</b>\n"

    # Direct link in message body
    links_block = f'<a href="{e(url)}">View Job</a>'

    # Build the message with Country, Work Type (On-site / Hybrid / Remote), Company, and Date
    lines = [
        f"{flag} {score_badge}🆕 <b>{title}</b>",
        f"🏢 {comp}",
        f"📍 {loc}",
        f"🌍 {e(country)}  •  {wt_badge}",
        f"🕐 Posted {posted}",
        links_block,
    ]

    # Clean inline buttons:
    # 1. Direct Apply Job
    # 2. Referral Button (instead of the redundant LinkedIn button)
    company_name = job.company or ""
    if company_name and company_name.lower() not in ["company", "confidential"]:
        ref_query = quote(f"{company_name} recruiter OR engineer")
    else:
        ref_query = quote(f"{job.title} recruiter")
    referral_url = f"https://www.linkedin.com/search/results/people/?keywords={ref_query}&origin=GLOBAL_SEARCH_HEADER"

    keyboard = [
        [
            {"text": "⚡ Apply Job", "url": url},
            {"text": "🤝 Referral", "url": referral_url}
        ]
    ]

    _post("sendMessage", chat_id=config.TELEGRAM_CHAT_ID, text="\n".join(lines), parse_mode="HTML",
          disable_web_page_preview=True,
          reply_markup={"inline_keyboard": keyboard})

def get_chat_id():
    data = requests.get(API.format(config.TELEGRAM_TOKEN, "getUpdates"), timeout=20).json()
    for upd in reversed(data.get("result", [])):
        msg = upd.get("message") or upd.get("channel_post")
        if msg:
            return msg["chat"]["id"]
    return None

def send_document(path, caption=""):
    with open(path, "rb") as f:
        r = requests.post(API.format(config.TELEGRAM_TOKEN, "sendDocument"),
                          data={"chat_id": config.TELEGRAM_CHAT_ID, "caption": caption[:1000]},
                          files={"document": f}, timeout=60)
    r.raise_for_status()

def send_followup(job, extras):
    """
    إرسال ملف الـ CV المخصص كملف فقط عند تفعيله.
    تم إلغاء إرسال رسالة الريفرال النصية المنفصلة لأن الريفرال أصبح زر مباشر في نفس رسالة الوظيفة.
    """
    t = extras.get("tailored")
    if extras.get("docx"):
        cap = f"📄 CV مخصص لـ {job.title}"
        if t:
            cap += f"\n🎯 Match: {int(t.get('match_score', 0))}%"
            if t.get("missing_keywords"):
                cap += "\n⚠️ مش عندك: " + ", ".join(t["missing_keywords"][:6])
        send_document(extras["docx"], cap[:1000])
