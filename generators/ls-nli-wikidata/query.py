"""Ask Wikidata for the items of the VIAF and LC numbers of nli-records (makes the input of ls-nli-wikidata).

python3 query.py <nli-records.ttl.gz> <out dir>

Reads the owl:sameAs links of the records to VIAF and to the LC name authority file, and asks the Wikidata Query
Service, in batches of BATCH numbers (POST, one request every few seconds), for the items that state them: P214
(VIAF ID) and P244 (Library of Congress authority ID). Writes p214.rq and p244.rq (the query, with VALUES_ as the
place of the numbers) and p214.tsv and p244.tsv (number, item; one row per pair, sorted).
"""

import csv
import io
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from jl.fetch import request  # noqa: E402
from jl.rdf import read_triples  # noqa: E402

WDQS = "https://query.wikidata.org/sparql"
BATCH = 4000
SAME = "http://www.w3.org/2002/07/owl#sameAs"
KEYS = {"p214": ("http://viaf.org/viaf/", "P214"), "p244": ("http://id.loc.gov/authorities/names/", "P244")}
QUERY = "SELECT ?id ?item WHERE {{ VALUES ?id {{ VALUES_ }} ?item wdt:{prop} ?id . }}\n"


def numbers(path):
    out = {k: set() for k in KEYS}
    for s, p, o in read_triples(path):
        if p == SAME:
            for k, (prefix, _) in KEYS.items():
                if o.startswith(prefix):
                    out[k].add(o[len(prefix):])
    return out


def ask(query, tries=5):
    data = urllib.parse.urlencode({"query": query}).encode()
    for i in range(tries):
        try:
            req = request(WDQS, data=data, headers={"Accept": "text/tab-separated-values",
                                                    "Content-Type": "application/x-www-form-urlencoded"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            if i + 1 == tries:
                raise
            print(f"  retry {i + 1} after {e}", flush=True)
            time.sleep(20 * (i + 1))


def main(src, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for key, ids in numbers(src).items():
        prop = KEYS[key][1]
        template = QUERY.format(prop=prop)
        (out / f"{key}.rq").write_text(template, encoding="utf-8")
        ids = sorted(ids)
        rows = set()
        for i in range(0, len(ids), BATCH):
            chunk = ids[i:i + BATCH]
            values = " ".join('"' + x.replace('"', "") + '"' for x in chunk)
            answer = ask(template.replace("VALUES_", values))
            for row in csv.reader(io.StringIO(answer), delimiter="\t"):
                if row and row[0] != "?id":
                    rows.add((row[0].strip('"'), row[1].strip("<>").rsplit("/", 1)[-1]))
            print(f"{key}: {min(i + BATCH, len(ids)):,} of {len(ids):,} numbers, {len(rows):,} pairs", flush=True)
            time.sleep(3)
        with open(out / f"{key}.tsv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n")
            w.writerow(["id", "item"])
            w.writerows(sorted(rows))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
