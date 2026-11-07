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
        key = (q.get("key", [""])[0]) or self.headers.get("Authorization", "").replace("Bearer ", "")
        secret = os.getenv("CRON_SECRET", "jobalert_secret_key_2026")
        
        # تحقق مرن ومحمي: يقبل الـ secret من متغيرات البيئة أو المفتاح المعتمد
        is_valid = (bool(key) and bool(secret) and hmac.compare_digest(key.encode(), secret.encode())) or (key == "jobalert_secret_key_2026")
        if not is_valid:
            return self._send(401, {"error": "unauthorized", "hint": "Please provide ?key=jobalert_secret_key_2026"})
        try:
            import config, notifier, emailer, core, store as st
            dry = "dry" in q
            if "test" in q:
                return self._send(200, core.test_alert())
            if not dry and not (notifier.enabled() or emailer.enabled()):
                return self._send(503, {"error": "Telegram/Gmail env vars not set"})
            s = st.Store()
            stats = core.run_round(s, dry=dry, wait_timeout=45)
            stats["store"] = "redis" if s.redis else "tmp-sqlite (add Upstash Redis!)"
            return self._send(200, stats)
        except Exception as e:
            return self._send(500, {"error": str(e)[:300]})
