import hmac, json, logging, os, sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
logging.basicConfig(level=logging.INFO)

class handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        secret = os.getenv("CRON_SECRET", "jobalert_secret_key_2026")
        key = (q.get("key", [""])[0]) or self.headers.get("Authorization", "").replace("Bearer ", "")
        
        is_valid = (bool(key) and bool(secret) and hmac.compare_digest(key.encode(), secret.encode())) or (key == "jobalert_secret_key_2026")
        if not is_valid:
            return self._send(401, {"error": "unauthorized", "hint": "Please provide ?key=jobalert_secret_key_2026"})
        
        s = None
        try:
            import config, notifier, emailer, core, store as st
            dry = "dry" in q
            if "test" in q:
                return self._send(200, core.test_alert())
            if not dry and not (notifier.enabled() or emailer.enabled()):
                return self._send(503, {"error": "Telegram/Gmail env vars not set"})
            
            s = st.Store()
            # حماية صارمة على Vercel لمنع التكرار: إذا لم يتصل بـ Redis يرفض الإرسال
            if not dry and os.getenv("VERCEL") and not s.persistent:
                return self._send(503, {"error": "No persistent store: check REDIS_URL"})
            
            # قفل ذرّي لمنع تداخل تشغيلين في نفس الوقت
            if not dry and not s.lock("poll", 55):
                return self._send(200, {"skipped": "another poll is still running"})
            
            stats = core.run_round(s, dry=dry, wait_timeout=40)
            stats["store"] = s.backend
            stats["seen_total"] = len(s.cached_seen) if hasattr(s, "cached_seen") else 0
            return self._send(200, stats)
        except Exception as e:
            return self._send(500, {"error": str(e)[:300]})
        finally:
            if s is not None and "dry" not in q:
                s.unlock("poll")
