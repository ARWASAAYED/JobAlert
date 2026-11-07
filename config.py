"""كل الإعدادات هنا. عدّلي اللي يناسبك."""
import os

# ---- Telegram (من متغيرات البيئة أو حطيهم هنا مباشرة) ----
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ---- التوقيت ----
POLL_SECONDS = 120          # الفحص كل كام ثانية (متنزلش عن 90 عشان لينكدان ميعملش بلوك)
MAX_AGE_MINUTES = 30        # بس الوظايف اللي نزلت في آخر X دقيقة

# ---- الفلاتر ----
# لازم العنوان يحتوي واحدة من دول
TITLE_MUST_ANY = ["react", "front-end", "front end", "frontend", "next.js", "nextjs"]
# ولازم "react" تظهر في العنوان أو الوصف
DESCRIPTION_MUST = ["react"]
# أي عنوان فيه دول يتشال
TITLE_EXCLUDE = [
    "senior", "sr.", "sr ", "lead", "principal", "staff", "manager", "head of",
    "architect", "director", "mid-level", "mid level", "intermediate", "expert",
    "full stack", "fullstack", "full-stack",   # شيلي السطر ده لو عايزة Full Stack كمان
    "mobile", "react native", "wordpress", "shopify", "unpaid",
]
# لو العنوان فيه دول ومفيهوش react يتشال
OTHER_FRAMEWORKS = ["angular", "vue", "svelte", "php", "laravel", ".net", "java ", "python"]

# أقصى سنين خبرة مقبولة (الحد الأدنى المطلوب في الإعلان)
MAX_YEARS_REQUIRED = 2

# عبارات في الوصف معناها الوظيفة مش ليكي (مقيدة بدولة معينة)
BAD_PHRASES = [
    "us only", "u.s. only", "us citizens", "u.s. citizens", "authorized to work in the united states",
    "must be located in the us", "must reside in the us", "eligible to work in the us",
    "uk only", "must be based in the uk", "right to work in the uk", "eu only",
    "must be located in canada", "canada only", "latam only", "must reside in",
]

# ---- مصادر لينكدان (من غير لوجين) ----
LINKEDIN_KEYWORDS = ["react", "frontend"]
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
