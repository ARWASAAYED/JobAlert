# JobAlert على Vercel + GitHub

## 1) GitHub
repo جديد (Private) ثم ارفعي كل محتويات الفولدر ده (مش الفولدر نفسه) في الـ root.
أو بالـ terminal:
```bash
git init && git add . && git commit -m "init"
git branch -M main && git remote add origin https://github.com/USERNAME/jobalert.git && git push -u origin main
```

## 2) Vercel
Import الـ repo (Framework: Other). بعدين Settings → Environment Variables:

| Name | Value |
|---|---|
| CRON_SECRET | أي كلمة سر طويلة (بتحمي الـ endpoint) |
| TELEGRAM_TOKEN / TELEGRAM_CHAT_ID | من BotFather |
| SMTP_USER / SMTP_APP_PASSWORD / EMAIL_TO | Gmail + App Password |
| ANTHROPIC_API_KEY | اختياري (CV مخصص) |

**Storage** تاب → Create → Upstash Redis (Free). بيضيف KV_REST_API_URL/TOKEN لوحده.
(من غيره البوت هيبعت وظايف مكررة.)

Redeploy بعد إضافة المتغيرات.

## 3) الجدولة
Vercel Hobby cron بيشتغل مرة واحدة بس في اليوم، فاستخدمي cron-job.org (مجاني):
- URL: `https://YOUR-APP.vercel.app/api/poll?key=CRON_SECRET`
- كل دقيقة (أو دقيقتين)

## اختبار
- `/api/poll?key=...&test=1` → تنبيه تجريبي على كل القنوات
- `/api/poll?key=...&dry=1` → تشغيل من غير إرسال

## حدود لازم تعرفيها
- Wuzzuf مقفول على Vercel (Cloudflare + مكتبة native). شغّليه محلياً لو عايزاه: `ENABLE_WUZZUF=1 python main.py`
- لينكدان ممكن يحجب IPs السيرفرات أكتر من IP بيتك (429). الـ endpoint بيرجع errors في الـ JSON.
- الدالة عندها 60 ثانية. التنبيه الفوري بيتبعت الأول، والـ CV المخصص بيتبعت بعده.
