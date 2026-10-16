"""Harvest the persons, organisations and places of schluesseldokumente.net (the input of the generator).

python3 harvest.py <work dir>      fetch (resumable: pages already there are kept)
python3 harvest.py <work dir> --bundle <out dir>

The site lists its records in the BEACON files (persons and organisations by GND number), the sitemaps and the place
list /ort; every record has a JSON-LD form (<address>.jsonld, schema.org). Fetched: the two BEACON files, the sitemaps
of persons, organisations and places, the place list, and the JSON-LD of every person (sitemap: by GND number or by
the site's own number), organisation (BEACON) and place (place list, a superset of the place sitemap). The pages are
kept unchanged under pages/<address>.jsonld; a page that fails is recorded with its HTTP status. --bundle writes the
input: the index files unchanged and jsonld.jsonl.gz, one line per address with the HTTP status and the page text
unchanged. One request per second; the User-Agent is the framework's (decision 0028).
"""

import gzip
import json
import re
import sys
import time
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from jl.fetch import get  # noqa: E402

SITE = "https://schluesseldokumente.net"
INDEX = {"beacon-person.txt": "/person/gnd/beacon", "beacon-organisation.txt": "/organisation/gnd/beacon",
         "sitemap.person.xml": "/sitemap.person.xml", "sitemap.organization.xml": "/sitemap.organization.xml",
         "sitemap.place.xml": "/sitemap.place.xml", "ort.html": "/ort"}


def fetch(url):
    """(status, body)"""
    try:
        body = get(url)
        return 200, body
    except urllib.error.HTTPError as e:
        return e.code, b""
    finally:
        time.sleep(1)


def addresses(work):
    idx = work / "index"
    beacon = lambda f: [x.strip() for x in (idx / f).read_text(encoding="utf-8").splitlines()
                        if x.strip() and not x.startswith("#")]
    sitemap = lambda f: [re.sub(r"^https?://[^/]+", "", u) for u in
                         re.findall(r"<loc>([^<]+)</loc>", (idx / f).read_text(encoding="utf-8"))]
    out = set(sitemap("sitemap.person.xml"))
    out |= {f"/person/gnd/{x}" for x in beacon("beacon-person.txt")}
    out |= set(sitemap("sitemap.organization.xml"))
    out |= {f"/organisation/gnd/{x}" for x in beacon("beacon-organisation.txt")}
    out |= set(sitemap("sitemap.place.xml"))
    out |= set(re.findall(r'href="(/ort/tgn/[^"]+)"', (idx / "ort.html").read_text(encoding="utf-8")))
    return sorted(out)


def harvest(work):
    idx = work / "index"
    idx.mkdir(parents=True, exist_ok=True)
    for name, path in INDEX.items():
        if not (idx / name).exists():
            status, body = fetch(SITE + path)
            if status != 200:
                sys.exit(f"{path}: HTTP {status}")
            (idx / name).write_bytes(body)
    todo = addresses(work)
    print(f"{len(todo)} records", flush=True)
    for n, a in enumerate(todo, 1):
        page = work / "pages" / (a.lstrip("/") + ".jsonld")
        err = page.with_suffix(".error")
        if page.exists() or err.exists():
            continue
        page.parent.mkdir(parents=True, exist_ok=True)
        status, body = fetch(SITE + a + ".jsonld")
        if status == 200:
            page.write_bytes(body)
        else:
            err.write_text(f"{status}\n")
        if n % 100 == 0:
            print(f"  {n} of {len(todo)}", flush=True)
    print("done", flush=True)


def bundle(work, out):
    out.mkdir(parents=True, exist_ok=True)
    for name in INDEX:
        (out / name).write_bytes((work / "index" / name).read_bytes())
    n = errors = 0
    with gzip.open(out / "jsonld.jsonl.gz", "wt", encoding="utf-8") as f:
        for a in addresses(work):
            page = work / "pages" / (a.lstrip("/") + ".jsonld")
            if page.exists():
                rec = {"address": a, "status": 200, "text": page.read_text(encoding="utf-8")}
            else:
                err = page.with_suffix(".error")
                rec = {"address": a, "status": int(err.read_text()) if err.exists() else None, "text": None}
                errors += 1
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
            n += 1
    print(f"{n} records, {errors} without a page", flush=True)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        harvest(Path(sys.argv[1]))
    elif len(sys.argv) == 4 and sys.argv[2] == "--bundle":
        bundle(Path(sys.argv[1]), Path(sys.argv[3]))
    else:
        sys.exit(__doc__)
