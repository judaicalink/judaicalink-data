"""Fetch the BEACON of the Biographisches Portal der Rabbiner and, for every GND number in it, the portal page it
leads to (input of the bhr generator).

python3 fetch_portal.py <out dir>

The BEACON (https://www.steinheim-institut.de/daten/projekte/work3/beacon.txt) lists GND numbers with the target
bhr?gnd={ID}; the page there names the BHR id (<input name="id" value="NNNN">) and the person. Saves beacon.txt
unchanged, gnd/<GND number>.html unchanged (pages already there are kept), and gnd-bhr.tsv: GND number, BHR id (as
the portal gives it, zero-padded), the heading of the page. One request per second; the User-Agent is the
framework's (decision 0028).
"""

import html
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from jl.fetch import get  # noqa: E402

BEACON = "https://www.steinheim-institut.de/daten/projekte/work3/beacon.txt"
PAGE = "https://www.steinheim-institut.de/cgi-bin/bhr?gnd="


def page_id(text):
    m = re.search(r'<input type="hidden" name="id" value="(\d*)"', text)
    h = re.search(r"<h3>(.*?)</h3>", text, re.S)
    return (m.group(1) if m else ""), (html.unescape(re.sub(r"\s+", " ", h.group(1))).strip() if h else "")


def main(out):
    out = Path(out)
    (out / "gnd").mkdir(parents=True, exist_ok=True)
    beacon = out / "beacon.txt"
    if not beacon.exists():
        beacon.write_bytes(get(BEACON))
        time.sleep(1)
    gnds = []
    for line in beacon.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and line not in gnds:
            gnds.append(line)
    rows = []
    for i, g in enumerate(gnds, 1):
        path = out / "gnd" / f"{g}.html"
        if not path.exists():
            path.write_bytes(get(PAGE + g))
            time.sleep(1)
        rows.append((g, *page_id(path.read_text(encoding="utf-8", errors="replace"))))
        if i % 100 == 0:
            print(f"  {i} of {len(gnds)}", flush=True)
    with open(out / "gnd-bhr.tsv", "w", encoding="utf-8") as f:
        f.write("gnd\tbhr\theading\n")
        for r in sorted(rows):
            f.write("\t".join(r) + "\n")
    print(f"{len(gnds)} GND numbers; {sum(1 for r in rows if r[1])} with a BHR id", flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
