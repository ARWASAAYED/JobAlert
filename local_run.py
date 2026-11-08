"""تشغيل محلي (اختياري): python local_run.py   |   --dry لتجربة من غير إرسال"""
import argparse, logging, random, time
from concurrent.futures import ThreadPoolExecutor
import config, core
from store import Store

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--once", action="store_true"); p.add_argument("--dry", action="store_true")
    a = p.parse_args()
    store, pool = Store(), ThreadPoolExecutor(max_workers=3)
    while True:
        print(core.run_round(store, dry=a.dry, pool=pool, wait_timeout=120 if a.once else None))
        if a.once: break
        time.sleep(config.POLL_SECONDS + random.randint(0, 20))

if __name__ == "__main__":
    main()
