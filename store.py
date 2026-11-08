"""ذاكرة الوظايف المتشافة: Redis Cloud (دائم وعالمي) أو Upstash أو SQLite."""
import os, sqlite3, time, json, logging
import datetime as dt
import config

log = logging.getLogger("jobalert.store")

# احتفاظ بالمعرفات لمدة 90 يوماً لمنع أي تكرار نهائياً
SEEN_TTL = 90 * 86400

DEFAULT_REDIS_URL = "redis://default:jyxFrH1Es7SIadD7SAKP3tTOwh4hpgmW@neocozy-star-steadfast-83525.db.redis.io:11692"

class Store:
    def __init__(self):
        self.redis_client = None
        self.redis = False
        self.error_msg = ""
        self.cached_seen = set()

        # 1. الاتصال المباشر بـ Redis Cloud عبر REDIS_URL
        redis_url = os.getenv("REDIS_URL") or getattr(config, "REDIS_URL", None) or DEFAULT_REDIS_URL
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True
                )
                self.redis_client.ping()
                self.redis = True
                try:
                    self.cached_seen = set(self.redis_client.smembers("jobalert:seen_ids"))
                except Exception:
                    self.cached_seen = set()
                log.info("Connected to Redis Cloud successfully. Preloaded %d seen keys.", len(self.cached_seen))
            except Exception as e:
                self.error_msg = str(e)
                log.warning("Direct Redis connection failed: %s", e)
                self.redis_client = None
                self.redis = False

        # 2. فحص Upstash REST API كبديل
        if not self.redis:
            self.rest_url = os.getenv("KV_REST_API_URL") or os.getenv("UPSTASH_REDIS_REST_URL")
            self.rest_token = os.getenv("KV_REST_API_TOKEN") or os.getenv("UPSTASH_REDIS_REST_TOKEN")
            if self.rest_url and self.rest_token:
                self.redis = True

        # 3. محلياً: SQLite fallback
        if not self.redis:
            self.db = sqlite3.connect(config.DB_PATH, check_same_thread=False)
            self.db.execute("CREATE TABLE IF NOT EXISTS seen (key TEXT PRIMARY KEY, ts INTEGER)")

    def has(self, key):
        """فحص هل الوظيفة تمت معالجتها وإرسالها مسبقاً لمنع أي تكرار."""
        if key in self.cached_seen:
            return True
        if self.redis_client:
            try:
                exists = bool(self.redis_client.exists(f"seen:{key}")) or bool(self.redis_client.sismember("jobalert:seen_ids", key))
                if exists:
                    self.cached_seen.add(key)
                return exists
            except Exception as e:
                log.warning("Redis has() check error: %s", e)
        if getattr(self, "rest_url", None) and getattr(self, "rest_token", None):
            try:
                import requests
                r = requests.post(self.rest_url, headers={"Authorization": f"Bearer {self.rest_token}"},
                                  json=["EXISTS", f"seen:{key}"], timeout=5)
                return int(r.json().get("result") or 0) == 1
            except Exception:
                pass
        if hasattr(self, "db"):
            return self.db.execute("SELECT 1 FROM seen WHERE key=?", (key,)).fetchone() is not None
        return False

    def add(self, key, job=None):
        """تسجيل الوظيفة في الذاكرة الدائمة حتى لا تتكرر أبداً."""
        self.cached_seen.add(key)
        if self.redis_client:
            try:
                pipe = self.redis_client.pipeline()
                pipe.set(f"seen:{key}", "1", ex=SEEN_TTL)
                pipe.sadd("jobalert:seen_ids", key)
                if job:
                    job_data = {
                        "id": getattr(job, "id", key),
                        "source": getattr(job, "source", ""),
                        "title": getattr(job, "title", ""),
                        "company": getattr(job, "company", ""),
                        "location": getattr(job, "location", ""),
                        "country": getattr(job, "country", ""),
                        "work_type": getattr(job, "work_type", ""),
                        "score": getattr(job, "score", 0),
                        "url": getattr(job, "url", ""),
                        "posted_at": getattr(job, "posted_at", ""),
                        "matched_at": dt.datetime.now().isoformat()
                    }
                    pipe.lpush("jobalert:jobs_feed", json.dumps(job_data, ensure_ascii=False))
                    pipe.ltrim("jobalert:jobs_feed", 0, 99)
                pipe.execute()
                return
            except Exception as e:
                log.warning("Redis add() error: %s", e)
        if getattr(self, "rest_url", None) and getattr(self, "rest_token", None):
            try:
                import requests
                requests.post(self.rest_url, headers={"Authorization": f"Bearer {self.rest_token}"},
                              json=["SET", f"seen:{key}", "1", "EX", str(SEEN_TTL)], timeout=5)
            except Exception:
                pass
        if hasattr(self, "db"):
            try:
                self.db.execute("INSERT OR IGNORE INTO seen VALUES (?,?)", (key, int(time.time())))
                self.db.commit()
            except Exception:
                pass

    def remove(self, key):
        self.cached_seen.discard(key)
        if self.redis_client:
            try:
                self.redis_client.delete(f"seen:{key}")
                self.redis_client.srem("jobalert:seen_ids", key)
                return
            except Exception:
                pass
        if hasattr(self, "db"):
            try:
                self.db.execute("DELETE FROM seen WHERE key=?", (key,))
                self.db.commit()
            except Exception:
                pass

    def get_live_feed(self, limit=50):
        """استرجاع أحدث الوظائف الحقيقية المخزنة في Redis للداشبورد."""
        if self.redis_client:
            try:
                raw_items = self.redis_client.lrange("jobalert:jobs_feed", 0, limit - 1)
                return [json.loads(item) for item in raw_items if item]
            except Exception as e:
                log.warning("Redis get_live_feed error: %s", e)
        return []
