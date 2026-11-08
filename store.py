"""ذاكرة الوظايف المتشافة. claim() ذرّية: أول واحد ياخد الوظيفة والباقي بيتجاهلها، فمفيش تكرار أبداً.
الأولوية: REDIS_URL (redis-py) ثم Upstash REST ثم SQLite (محلي بس)."""
import os, sqlite3, time, json, logging
import config

log = logging.getLogger("jobalert.store")

# احتفاظ بالمعرفات لمدة 30 يوماً لمنع أي تكرار نهائياً
TTL = 30 * 86400

class Store:
    def __init__(self):
        self.backend = None
        self.error_msg = ""
        self.cached_seen = set()
        self.r = None

        # 1. الاتصال المباشر بـ Redis Cloud عبر REDIS_URL
        if config.REDIS_URL:
            try:
                import redis
                self.r = redis.Redis.from_url(
                    config.REDIS_URL,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True
                )
                self.r.ping()
                self.backend = "redis"
                try:
                    self.cached_seen = set(self.r.smembers("jobalert:seen_ids"))
                except Exception:
                    self.cached_seen = set()
                log.info("Connected to Redis Cloud successfully. Preloaded %d seen keys.", len(self.cached_seen))
            except Exception as e:
                self.error_msg = str(e)
                log.warning("Direct Redis connection failed: %s", e)
                self.r = None

        # 2. فحص Upstash REST API كبديل
        if not self.backend:
            self.url = os.getenv("KV_REST_API_URL") or os.getenv("UPSTASH_REDIS_REST_URL")
            self.token = os.getenv("KV_REST_API_TOKEN") or os.getenv("UPSTASH_REDIS_REST_TOKEN")
            if self.url and self.token:
                self.backend = "rest"

        # 3. محلياً: SQLite fallback
        if not self.backend:
            self.db = sqlite3.connect(config.DB_PATH, check_same_thread=False)
            self.db.execute("CREATE TABLE IF NOT EXISTS seen (key TEXT PRIMARY KEY, ts INTEGER)")
            self.backend = "sqlite"

    @property
    def persistent(self):
        return self.backend in ("redis", "rest")

    @property
    def redis(self):
        return self.persistent

    def _rest(self, *args):
        import requests
        r = requests.post(self.url, headers={"Authorization": f"Bearer {self.token}"},
                          json=[str(a) for a in args], timeout=8)
        r.raise_for_status()
        return r.json().get("result")

    def has(self, key):
        """فحص سريع بـ 0ms من الذاكرة ثم من Redis لمنع أي تكرار."""
        if key in self.cached_seen:
            return True
        k = "seen:" + key
        if self.backend == "redis":
            try:
                exists = bool(self.r.exists(k)) or bool(self.r.sismember("jobalert:seen_ids", key))
                if exists:
                    self.cached_seen.add(key)
                return exists
            except Exception as e:
                log.warning("Redis exists error: %s", e)
        if self.backend == "rest":
            try:
                return int(self._rest("EXISTS", k) or 0) == 1
            except Exception:
                pass
        if hasattr(self, "db"):
            return self.db.execute("SELECT 1 FROM seen WHERE key=?", (key,)).fetchone() is not None
        return False

    def claim(self, key):
        """حجز ذرّي (Atomic Lock): أول عملية فحص تاخد الوظيفة والباقي يتجاهلها فوراً."""
        self.cached_seen.add(key)
        k = "seen:" + key
        if self.backend == "redis":
            try:
                pipe = self.r.pipeline()
                pipe.set(k, "1", nx=True, ex=TTL)
                pipe.sadd("jobalert:seen_ids", key)
                res = pipe.execute()
                return bool(res[0])
            except Exception as e:
                log.warning("Redis claim error: %s", e)
                return False
        if self.backend == "rest":
            try:
                return self._rest("SET", k, "1", "NX", "EX", TTL) == "OK"
            except Exception:
                return False
        if hasattr(self, "db"):
            cur = self.db.execute("INSERT OR IGNORE INTO seen VALUES (?,?)", (key, int(time.time())))
            self.db.commit()
            return cur.rowcount == 1
        return True

    def add(self, key, job=None):
        """تسجيل الوظيفة كمتشافة (للوظائف المستبعدة بالفلاتر)."""
        self.cached_seen.add(key)
        k = "seen:" + key
        if self.backend == "redis":
            try:
                pipe = self.r.pipeline()
                pipe.set(k, "1", ex=TTL)
                pipe.sadd("jobalert:seen_ids", key)
                pipe.execute()
                return
            except Exception as e:
                log.warning("Redis add error: %s", e)
        elif self.backend == "rest":
            try:
                self._rest("SET", k, "1", "EX", TTL)
            except Exception:
                pass
        if hasattr(self, "db"):
            try:
                self.db.execute("INSERT OR IGNORE INTO seen VALUES (?,?)", (key, int(time.time())))
                self.db.commit()
            except Exception:
                pass

    def remove(self, key):
        """إلغاء التسجيل فقط إذا فشل إرسال التنبيه التقني لإعادة المحاولة."""
        self.cached_seen.discard(key)
        k = "seen:" + key
        if self.backend == "redis":
            try:
                self.r.delete(k)
                self.r.srem("jobalert:seen_ids", key)
            except Exception:
                pass
        elif self.backend == "rest":
            try:
                self._rest("DEL", k)
            except Exception:
                pass
        if hasattr(self, "db"):
            try:
                self.db.execute("DELETE FROM seen WHERE key=?", (key,))
                self.db.commit()
            except Exception:
                pass

    def record(self, job):
        """حفظ آخر 200 وظيفة تم إرسالها لعرضها بالداشبورد في Redis."""
        if self.backend != "redis":
            return
        try:
            job_data = {
                "key": job.key, "id": getattr(job, "id", job.key), "title": job.title,
                "source": getattr(job, "source", "unknown"),
                "company": job.company, "location": job.location, "url": job.url,
                "posted_text": getattr(job, "posted_text", "") or "Just now",
                "posted_at": getattr(job, "posted_at", ""),
                "description": getattr(job, "description", "") or f"{job.title} at {job.company}",
                "score": getattr(job, "score", 0), "match_score": getattr(job, "score", 0),
                "verdict": getattr(job, "verdict", "Good Fit"),
                "matched_keywords": getattr(job, "strengths", ["React", "Frontend"]),
                "missing_keywords": getattr(job, "gaps", []),
                "cv_suggestions": getattr(job, "cv_suggestions", []),
                "remote": getattr(job, "remote_search", False) or "remote" in getattr(job, "work_type", "").lower(),
                "work_type": getattr(job, "work_type", "On-site"),
                "country": getattr(job, "country", ""),
                "salary": getattr(job, "salary", ""), "recruiter": getattr(job, "recruiter", ""),
                "career_level": getattr(job, "career_level", ""),
                "sent_at": int(time.time())
            }
            pipe = self.r.pipeline()
            pipe.lpush("jobalert:jobs_feed", json.dumps(job_data, ensure_ascii=False))
            pipe.ltrim("jobalert:jobs_feed", 0, 199)
            pipe.lpush("recent_jobs", json.dumps(job_data, ensure_ascii=False))
            pipe.ltrim("recent_jobs", 0, 199)
            pipe.execute()
        except Exception as e:
            log.warning("Redis record error: %s", e)

    def lock(self, name="poll", ttl=55):
        """قفل لمنع تداخل مرتين فحص في نفس الوقت."""
        k = "lock:" + name
        if self.backend == "redis":
            try:
                return bool(self.r.set(k, "1", nx=True, ex=ttl))
            except Exception:
                return True
        if self.backend == "rest":
            try:
                return self._rest("SET", k, "1", "NX", "EX", ttl) == "OK"
            except Exception:
                return True
        return True

    def unlock(self, name="poll"):
        """فك قفل الفحص."""
        k = "lock:" + name
        try:
            if self.backend == "redis":
                self.r.delete(k)
            elif self.backend == "rest":
                self._rest("DEL", k)
        except Exception:
            pass

    def get_live_feed(self, limit=50):
        if self.backend == "redis":
            try:
                raw_items = self.r.lrange("jobalert:jobs_feed", 0, limit - 1)
                return [json.loads(item) for item in raw_items if item]
            except Exception as e:
                log.warning("Redis get_live_feed error: %s", e)
        return []
