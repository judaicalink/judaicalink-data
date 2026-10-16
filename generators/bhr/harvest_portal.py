"""Harvest every entry of the Biographisches Portal der Rabbiner (input of the bhr generator).

python3 harvest_portal.py <out dir>

Fetches https://www.steinheim-institut.de/cgi-bin/bhr?id=<n> for n = 1, 2, … and saves each answer unchanged as
id/<n>.html (pages already there are kept, so an interrupted harvest continues). The portal answers "Eintrag nicht
vorhanden" for a number without an entry; the harvest stops after STOP such numbers in a row above the highest entry
seen. Writes harvest.tsv: number, whether there is an entry, the heading of the page. Also saves the BEACON
(beacon.txt) unchanged. One request per second; the User-Agent is the framework's (decision 0028).
"""

import html
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from jl.fetch import get  # noqa: E402

PAGE = "https://www.steinheim-institut.de/cgi-bin/bhr?id="
BEACON = "https://www.steinheim-institut.de/daten/projekte/work3/beacon.txt"
NO_ENTRY = "Eintrag nicht vorhanden"
STOP = 50


def heading(text):
    h = re.search(r"<h3>(.*?)</h3>", text, re.S)
    return html.unescape(re.sub(r"<[^>]+>|\s+", " ", h.group(1))).strip() if h else ""


def main(out):
    out = Path(out)
    (out / "id").mkdir(parents=True, exist_ok=True)
    if not (out / "beacon.txt").exists():
        (out / "beacon.txt").write_bytes(get(BEACON))
        time.sleep(1)
    rows, n, misses = [], 0, 0
    while misses < STOP:
        n += 1
        path = out / "id" / f"{n}.html"
        if not path.exists():
            path.write_bytes(get(PAGE + str(n)))
            time.sleep(1)
        text = path.read_text(encoding="utf-8", errors="replace")
        entry = NO_ENTRY not in text
        misses = 0 if entry else misses + 1
        rows.append((n, entry, heading(text) if entry else ""))
        if n % 100 == 0:
            print(f"  {n}: {sum(1 for r in rows if r[1])} entries", flush=True)
    with open(out / "harvest.tsv", "w", encoding="utf-8") as f:
        f.write("id\tentry\theading\n")
        for i, e, h in rows:
            f.write(f"{i}\t{'yes' if e else 'no'}\t{h}\n")
    print(f"{n} numbers fetched, {sum(1 for r in rows if r[1])} entries", flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
