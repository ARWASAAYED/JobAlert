"""ذاكرة الوظايف المتشافة: Upstash Redis (على Vercel) أو SQLite (محلياً)."""
import os, sqlite3, time, requests
import config

TTL = 3 * 86400

class Store:
    def __init__(self):
        self.url = os.getenv("KV_REST_API_URL") or os.getenv("UPSTASH_REDIS_REST_URL")
        self.token = os.getenv("KV_REST_API_TOKEN") or os.getenv("UPSTASH_REDIS_REST_TOKEN")
        self.redis = bool(self.url and self.token)
        if not self.redis:
            self.db = sqlite3.connect(config.DB_PATH, check_same_thread=False)
            self.db.execute("CREATE TABLE IF NOT EXISTS seen (key TEXT PRIMARY KEY, ts INTEGER)")

    def _cmd(self, *args):
        r = requests.post(self.url, headers={"Authorization": f"Bearer {self.token}"},
                          json=[str(a) for a in args], timeout=10)
        r.raise_for_status()
        return r.json().get("result")

    def has(self, key):
        if self.redis:
            return int(self._cmd("EXISTS", "seen:" + key) or 0) == 1
        return self.db.execute("SELECT 1 FROM seen WHERE key=?", (key,)).fetchone() is not None

    def add(self, key):
        if self.redis:
            self._cmd("SET", "seen:" + key, "1", "EX", TTL)
        else:
            self.db.execute("INSERT OR IGNORE INTO seen VALUES (?,?)", (key, int(time.time()))); self.db.commit()

    def remove(self, key):
        if self.redis:
            self._cmd("DEL", "seen:" + key)
        else:
            self.db.execute("DELETE FROM seen WHERE key=?", (key,)); self.db.commit()
