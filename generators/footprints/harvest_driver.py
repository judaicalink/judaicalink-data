"""Run the Footprints harvest until it is complete; after a stop (throttle), wait and try again with varying delays,
and record per attempt the delay before it and how many pages it got (to learn which delays work).

nohup python3 generators/footprints/harvest_driver.py > /dev/null 2>&1 &   (from judaicalink-data; the paths below)
"""

import datetime
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = Path("/Users/kai/lokal/judaicalink/work/footprints-harvest")
LOG = Path("/Users/kai/lokal/judaicalink/work/footprints-harvest.log")
REPORT = Path("/Users/kai/lokal/judaicalink/work/footprints-retry.tsv")
DELAYS = [10]   # minutes before a restart (decided 2026-10-17)


def pages():
    return sum(1 for _ in (OUT / "pages").rglob("*.json")) + sum(1 for _ in (OUT / "fill").rglob("*.json"))


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(args):
    with open(LOG, "a") as log:
        log.write(f"--- driver {now()}: harvest.py {' '.join(args)}\n")
        log.flush()
        return subprocess.run([sys.executable, "generators/footprints/harvest.py", str(OUT), *args], cwd=REPO,
                              stdout=log, stderr=subprocess.STDOUT).returncode


def until_done(args, label):
    attempt, delay = 0, 0
    while True:
        before, start = pages(), now()
        code = run(args)
        got = pages() - before
        with open(REPORT, "a") as r:
            r.write(f"{label}\t{attempt}\t{start}\t{delay}\t{got}\t{'done' if code == 0 else 'stopped'}\n")
        if code == 0:
            return
        delay = DELAYS[attempt % len(DELAYS)]
        attempt += 1
        time.sleep(delay * 60)


if __name__ == "__main__":
    if not REPORT.exists():
        REPORT.write_text("step\tattempt\tstarted\tdelay_before_min\tpages_got\tresult\n")
    until_done([], "lists")
    until_done(["--fill"], "fill")
