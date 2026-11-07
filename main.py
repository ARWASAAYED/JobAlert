"""تشغيل محلي (اختياري): python main.py"""
import argparse, logging, random, time
from concurrent.futures import ThreadPoolExecutor
import config, notifier, emailer, core
from store import Store

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--once", action="store_true"); p.add_argument("--dry", action="store_true")
    p.add_argument("--test", action="store_true"); p.add_argument("--get-chat-id", action="store_true")
    a = p.parse_args()
    if a.get_chat_id: print("CHAT ID:", notifier.get_chat_id()); return
    if a.test: print(core.test_alert()); return
    if not a.dry and not (notifier.enabled() or emailer.enabled()):
        raise SystemExit("فعّلي تليجرام أو Gmail الأول")
    store, pool = Store(), ThreadPoolExecutor(max_workers=3)
    while True:
        print(core.run_round(store, dry=a.dry, pool=pool, wait_timeout=120 if a.once else None))
        if a.once: break
        time.sleep(config.POLL_SECONDS + random.randint(0, 20))

if __name__ == "__main__":
    main()
