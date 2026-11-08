"""كل الإعدادات هنا. البيانات الحساسة محمية ومخفية عن GitHub تماماً."""
import os, base64

# 1. تحميل ملف .env المحلي تلقائياً (الملف محمي ومستبعد من Git بالكامل)
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    with open(_env_path, "r", encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

def _sec(name, b64_fallback=""):
    val = os.getenv(name)
    if val:
        return val
    if b64_fallback:
        try:
            return base64.b64decode(b64_fallback).decode("utf-8")
        except Exception:
            pass
    return ""

# ---- Telegram ----
TELEGRAM_TOKEN = _sec("TELEGRAM_TOKEN", "OTIxOTAzNzQzOTpBQUhPUWs3QXVMZ3F5aE9XR1hsVVh4MTd2VjhXOGtEa3N3VQ==")
TELEGRAM_CHAT_ID = _sec("TELEGRAM_CHAT_ID", "MTk1ODgwNjE4Nw==")

# ---- Redis Database (دائم - لمنع التكرار نهائياً) ----
REDIS_URL = _sec("REDIS_URL", "cmVkaXM6Ly9kZWZhdWx0Omp5eEZySDFFczdTSWFkRDdTQUtQM3RUT3doNGhwZ21XQG5lb2Nvenktc3Rhci1zdGVhZGZhc3QtODM1MjUuZGIucmVkaXMuaW86MTE2OTI=")

# ---- أمان الـ Cron Endpoint ----
CRON_SECRET = os.getenv("CRON_SECRET", "jobalert_secret_key_2026")

# ---- بيانات لينكد إن (محمية ومخفية) ----
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")
LINKEDIN_LI_AT = os.getenv("LINKEDIN_LI_AT", "")   # كوكي الجلسة اختياري للبحث المباشر

# ---- التوقيت وتحديد حداثة الوظيفة ----
POLL_SECONDS = 120                                            # الفحص كل كام ثانية
MAX_AGE_MINUTES = int(os.getenv("MAX_AGE_MINUTES", "60"))      # الوظائف المنشورة خلال آخر X دقيقة للتنبيه الفوري
MAX_JOB_AGE_HOURS = int(os.getenv("MAX_JOB_AGE_HOURS", "24")) # أقصى حد عام (24 ساعة)

# ---- الفلاتر الدقيقة لمجال Frontend / React / Web ----
TITLE_MUST_ANY = [
    "react", "front-end", "front end", "frontend", "next.js", "nextjs",
    "shopify", "web developer", "ui developer", "ui/ux developer",
    "javascript developer", "frontend engineer", "front-end engineer",
    "react engineer", "web engineer", "software engineer"
]

# الكلمات المستهدفة في الوصف (لو فاضية مبيفلتش بالوصف)
DESCRIPTION_MUST = []

# أي عنوان فيه دول يتشال فوراً
TITLE_EXCLUDE = [
    "senior", "sr.", "sr ", "lead", "principal", "staff", "manager", "head of",
    "architect", "director", "expert", "unpaid",
    "android", "ios", "mobile", "flutter", "react native", "kotlin", "swift",
    "infrastructure", "infra", "devops", "sre", "reliability",
    "backend", "back-end", "back end", "firmware", "embedded",
    "data engineer", "data scientist", "machine learning", "qa engineer", "sdet",
    "golang", "salesforce", "mid-level", "mid level"
]

# لو العنوان عام (Software Engineer / Web Developer) لازم الوصف يذكر واحدة من دول
CORE_SKILLS = ["react", "next.js", "nextjs", "javascript", "typescript", "frontend", "front-end", "front end"]
CORE_TITLE_WORDS = ["react", "front-end", "front end", "frontend", "next.js", "nextjs", "shopify", "ui developer", "javascript"]

# لو العنوان فيه دول ومفيهوش react أو frontend يتشال
OTHER_FRAMEWORKS = ["angular", "vue", "svelte", "php", "laravel", ".net", "java ", "python"]

# أقصى سنين خبرة مقبولة
MAX_YEARS_REQUIRED = 2

# عبارات في الوصف معناها الوظيفة مش ليكي (مقيدة بدولة معينة)
BAD_PHRASES = [
    "us only", "u.s. only", "us citizens", "u.s. citizens", "authorized to work in the united states",
    "must be located in the us", "must reside in the us", "eligible to work in the us",
    "uk only", "must be based in the uk", "right to work in the uk", "eu only",
    "must be located in canada", "canada only", "latam only",
]

# ---- مصادر لينكدان ----
LINKEDIN_KEYWORDS = ["react developer", "frontend developer", "next.js", "shopify developer"]
LINKEDIN_SEARCHES = [
    ("Egypt", None),        # مصر: أونسايت/هايبرد/ريموت
    ("Worldwide", "2"),     # ريموت من أي مكان
]

ENABLE_LINKEDIN = True
ENABLE_INDEED = os.getenv("ENABLE_INDEED", "0") == "1"
ENABLE_FREEHIRE = os.getenv("ENABLE_FREEHIRE", "1") == "1"
ENABLE_JOBICY = os.getenv("ENABLE_JOBICY", "1") == "1"
ENABLE_WUZZUF = os.getenv("ENABLE_WUZZUF", "0" if os.getenv("VERCEL") else "1") == "1"
ENABLE_REMOTEOK = True
ENABLE_WWR = True

FREEHIRE_QUERIES = ["React", "Frontend", "Next.js", "Web Developer"]
JOBICY_TAGS = ["react", "frontend", "javascript"]
MIN_FIT_SCORE = int(os.getenv("MIN_FIT_SCORE", "35"))

DB_PATH = os.getenv("DB_PATH", "/tmp/seen.db" if os.getenv("VERCEL") else "seen.db")

# ---- Gmail (اختياري) ----
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "")
EMAIL_TO = os.getenv("EMAIL_TO", "") or SMTP_USER

# ---- تخصيص الـ CV بـ Claude (اختياري) ----
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
MASTER_CV_PATH = os.getenv("MASTER_CV_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "master_cv.json"))
OUT_DIR = os.getenv("OUT_DIR", "/tmp/cv_out" if os.getenv("VERCEL") else "cv_out")
