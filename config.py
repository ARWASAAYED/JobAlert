"""كل الإعدادات هنا. عدّلي اللي يناسبك."""
import os

# ---- Telegram (من متغيرات البيئة أو حطيهم هنا مباشرة) ----
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "9219037439:AAHOQk7AuLgqyhOWGXlUXx17vV8W8kDkswU")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1958806187")

# ---- Redis Database (دائم - لمنع تكرار الرسائل نهائياً) ----
REDIS_URL = os.getenv("REDIS_URL", "redis://default:jyxFrH1Es7SIadD7SAKP3tTOwh4hpgmW@neocozy-star-steadfast-83525.db.redis.io:11692")

# ---- التوقيت وتحديد حداثة الوظيفة ----
POLL_SECONDS = 120                                            # الفحص كل كام ثانية
MAX_JOB_AGE_HOURS = int(os.getenv("MAX_JOB_AGE_HOURS", "24")) # أقصى عمر للوظيفة: 24 ساعة فقط (وظائف اليوم والحديثة)
MAX_AGE_MINUTES = int(os.getenv("MAX_AGE_MINUTES", "1440"))

# ---- الفلاتر الدقيقة لمجال Frontend / React / Web ----
# لازم العنوان يحتوي واحدة من دول حصراً
TITLE_MUST_ANY = [
    "react", "front-end", "front end", "frontend", "next.js", "nextjs",
    "shopify", "web developer", "ui developer", "ui/ux developer",
    "javascript developer", "frontend engineer", "front-end engineer",
    "react engineer", "web engineer"
]

# الكلمات المستهدفة في الوصف (لو فاضية مبيفلتش بالوصف)
DESCRIPTION_MUST = []

# أي عنوان فيه دول يتشال فوراً (استبعاد المناصب العليا ومجالات الموبايل والباك إند والإنفرا)
TITLE_EXCLUDE = [
    "senior", "sr.", "sr ", "lead", "principal", "staff", "manager", "head of",
    "architect", "director", "expert", "unpaid",
    "android", "ios", "mobile", "flutter", "react native",
    "infrastructure", "infra", "devops", "sre", "reliability",
    "backend", "back-end", "back end", "firmware", "embedded",
    "data engineer", "data scientist", "machine learning", "qa engineer", "sdet"
]

# لو العنوان فيه دول ومفيهوش react أو frontend يتشال
OTHER_FRAMEWORKS = ["angular", "vue", "svelte", "php", "laravel", ".net", "java ", "python"]

# أقصى سنين خبرة مقبولة (الحد الأدنى المطلوب في الإعلان)
MAX_YEARS_REQUIRED = 2

# عبارات في الوصف معناها الوظيفة مش ليكي (مقيدة بدولة معينة)
BAD_PHRASES = [
    "us only", "u.s. only", "us citizens", "u.s. citizens", "authorized to work in the united states",
    "must be located in the us", "must reside in the us", "eligible to work in the us",
    "uk only", "must be based in the uk", "right to work in the uk", "eu only",
    "must be located in canada", "canada only", "latam only",
]

# ---- مصادر لينكدان (من غير لوجين) ----
LINKEDIN_KEYWORDS = ["react developer", "frontend developer", "next.js", "shopify developer"]
# (المكان, فلتر نوع الشغل: None = الكل, "2" = ريموت)
LINKEDIN_SEARCHES = [
    ("Egypt", None),        # مصر: أونسايت/هايبرد/ريموت
    ("Worldwide", "2"),     # ريموت من أي مكان
]

ENABLE_LINKEDIN = True
ENABLE_INDEED = os.getenv("ENABLE_INDEED", "1") == "1"
ENABLE_FREEHIRE = os.getenv("ENABLE_FREEHIRE", "1") == "1"
ENABLE_JOBICY = os.getenv("ENABLE_JOBICY", "1") == "1"
ENABLE_WUZZUF = os.getenv("ENABLE_WUZZUF", "0" if os.getenv("VERCEL") else "1") == "1"
ENABLE_REMOTEOK = True
ENABLE_WWR = True

INDEED_SEARCHES = [
    {"term": "react developer", "location": "Cairo", "country": "egypt", "remote": False},
    {"term": "frontend developer", "location": "Cairo", "country": "egypt", "remote": False},
    {"term": "react developer", "location": "", "country": "usa", "remote": True},
]

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
