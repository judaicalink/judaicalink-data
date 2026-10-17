"""Harvest the Bibliografie deutsch-jüdische Geschichte Nordrhein-Westfalen (input of the nrwbibdjg generator).

python3 harvest.py <out dir>

Saves the BEACON (beacon.txt) and, for every GND number in it, the OPAC answer of the search by GND number
(gnd/<number>.html), unchanged; pages already there are kept, so an interrupted harvest continues. One request per
second; the User-Agent is the framework's (decision 0028).
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from jl.fetch import get  # noqa: E402

BEACON = "https://www.steinheim-institut.de/ebib-djg-nrw/ebib-djg-nrw-beacon.txt"
QUERY = "https://www.steinheim-institut.de/ebib-djg-nrw/query.html?database=NRW-Bibliografie&text1={}&kategorie1=gnd"


def main(out):
    out = Path(out)
    (out / "gnd").mkdir(parents=True, exist_ok=True)
    if not (out / "beacon.txt").exists():
        (out / "beacon.txt").write_bytes(get(BEACON))
        time.sleep(1)
    numbers = []
    for line in (out / "beacon.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and line not in numbers:
            numbers.append(line)
    for i, n in enumerate(numbers, 1):
        path = out / "gnd" / f"{n}.html"
        if not path.exists():
            path.write_bytes(get(QUERY.format(n)))
            time.sleep(1)
        if i % 100 == 0:
            print(f"  {i} of {len(numbers)}", flush=True)
    print(f"{len(numbers)} GND numbers", flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
