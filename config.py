"""كل الإعدادات هنا. عدّلي اللي يناسبك."""
import os

# ---- Telegram (من متغيرات البيئة أو حطيهم هنا مباشرة) ----
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "9219037439:AAHOQk7AuLgqyhOWGXlUXx17vV8W8kDkswU")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1958806187")

# ---- التوقيت ----
POLL_SECONDS = 120          # الفحص كل كام ثانية (متنزلش عن 90 عشان لينكدان ميعملش بلوك)
MAX_AGE_MINUTES = int(os.getenv("MAX_AGE_MINUTES", "1440"))  # فحص وظائف آخر 24 ساعة مع منع التكرار

# ---- الفلاتر ----
# لازم العنوان يحتوي واحدة من دول
TITLE_MUST_ANY = [
    "react", "front-end", "front end", "frontend", "next.js", "nextjs",
    "shopify", "web developer", "ui developer", "ui/ux developer",
    "javascript developer", "software engineer"
]
# الكلمات المستهدفة في الوصف (لو فاضية مبيفلتش بالوصف)
DESCRIPTION_MUST = []
# أي عنوان فيه دول يتشال (إلا لو مذكور junior صراحة)
TITLE_EXCLUDE = [
    "senior", "sr.", "sr ", "lead", "principal", "staff", "manager", "head of",
    "architect", "director", "expert", "unpaid"
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
ENABLE_WUZZUF = os.getenv("ENABLE_WUZZUF", "0" if os.getenv("VERCEL") else "1") == "1"
ENABLE_REMOTEOK = True
ENABLE_WWR = True

DB_PATH = os.getenv("DB_PATH", "/tmp/seen.db" if os.getenv("VERCEL") else "seen.db")

# ---- Gmail (اختياري) ----
# لازم 2-Step Verification + App Password (شوفي README)
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "")
EMAIL_TO = os.getenv("EMAIL_TO", "") or SMTP_USER

# ---- تخصيص الـ CV بـ Claude (اختياري) ----
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
MASTER_CV_PATH = os.getenv("MASTER_CV_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "master_cv.json"))
OUT_DIR = os.getenv("OUT_DIR", "/tmp/cv_out" if os.getenv("VERCEL") else "cv_out")
