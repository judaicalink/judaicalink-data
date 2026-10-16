"""Harvest the Footprints API in full (the input of the generator).

python3 harvest.py <out dir> [<endpoint> ...]
python3 harvest.py <out dir> --fill

Saves every page of every list endpoint unchanged as pages/<endpoint>/<page>.json (pages already there are kept, so
an interrupted harvest continues), then writes <endpoint>.jsonl.gz: the records by id, each once, and harvest.json:
per endpoint the count the API reported, the distinct ids found, and the time of the first and last page. The lists
are sorted by fields that are not unique (persons by name, footprints by title, copies by imprint), so paging can
skip or repeat records; a shortfall shows in harvest.json. --fill then fetches, one by one, the records that other
records refer to but the lists missed (persons of actors, works of imprints, imprints of copies, copies of
footprints) into fill/<endpoint>/<id>.json and adds them to <endpoint>.jsonl.gz. One request per second; the User-Agent is the
framework's (decision 0028), the one Footprints allowed.
"""

import datetime
import gzip
import json
import sys
import time
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from jl.fetch import get  # noqa: E402

API = "https://footprints.ctl.columbia.edu/api/"
# not digitalobject: the footprints carry their digital objects (name, description, URL), which we only link to
ENDPOINTS = ["writtenwork", "imprint", "book", "footprint", "person",
             "language", "role", "identifiertype", "digitalformat", "place", "actor"]


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def harvest(out, endpoint):
    pages = out / "pages" / endpoint
    pages.mkdir(parents=True, exist_ok=True)
    n, count, started = 1, None, now()
    while True:
        path = pages / f"{n:05d}.json"
        if path.exists():
            data = json.loads(path.read_bytes())
        else:
            body = get(f"{API}{endpoint}/?format=json&page={n}")
            data = json.loads(body)
            path.write_bytes(body)
            time.sleep(1)
        count = data.get("count", count)
        if n % 50 == 0:
            print(f"  {endpoint}: page {n} of {-(-count // 15)}", flush=True)
        if not data.get("next"):
            break
        n += 1
    return {"count": count, "distinct": len(assemble(out, endpoint)), "pages": n, "started": started,
            "finished": now()}


def assemble(out, endpoint):
    """The records of the pages and of fill/, by id, written to <endpoint>.jsonl.gz."""
    records = {}
    for p in sorted((out / "pages" / endpoint).glob("*.json")):
        for r in json.loads(p.read_bytes())["results"]:
            records[r["id"]] = r
    for p in sorted((out / "fill" / endpoint).glob("*.json")):
        r = json.loads(p.read_bytes())
        if "id" in r:
            records[r["id"]] = r
    with gzip.open(out / f"{endpoint}.jsonl.gz", "wt", encoding="utf-8") as f:
        for i in sorted(records):
            f.write(json.dumps(records[i], ensure_ascii=False, sort_keys=True) + "\n")
    return records


def records(out, endpoint):
    path = out / f"{endpoint}.jsonl.gz"
    return [json.loads(line) for line in gzip.open(path, "rt", encoding="utf-8")] if path.exists() else []


def referenced(out):
    """endpoint -> the ids other records refer to."""
    refs = {"person": set(), "writtenwork": set(), "imprint": set(), "book": set()}

    def actors(rs):
        for a in rs or []:
            if a.get("person"):
                refs["person"].add(a["person"]["id"])

    def imprint(i):
        if i:
            refs["imprint"].add(i["id"])
            actors(i.get("actor"))
            if i.get("work"):
                refs["writtenwork"].add(i["work"]["id"])
                actors(i["work"].get("actor"))

    for r in records(out, "writtenwork"):
        actors(r.get("actor"))
    for r in records(out, "imprint"):
        imprint(r)
    for r in records(out, "book"):
        imprint(r.get("imprint"))
        actors(r.get("owners"))
        actors(r.get("current_owners"))
    for r in records(out, "footprint"):
        actors(r.get("actor"))
        parts = str(r.get("book_copy_identifier") or "").split("-")   # work-imprint-copy
        if len(parts) == 3 and all(x.isdigit() for x in parts):
            refs["writtenwork"].add(int(parts[0]))
            refs["imprint"].add(int(parts[1]))
            refs["book"].add(int(parts[2]))
    return refs


def fill(out, report):
    for ep, ids in referenced(out).items():
        have = {r["id"] for r in records(out, ep)}
        missing = sorted(ids - have)
        d = out / "fill" / ep
        d.mkdir(parents=True, exist_ok=True)
        print(f"{ep}: {len(missing)} referenced but not listed", flush=True)
        for i in missing:
            path = d / f"{i}.json"
            if path.exists():
                continue
            try:
                path.write_bytes(get(f"{API}{ep}/{i}/?format=json"))
            except urllib.error.HTTPError as e:
                path.write_text(json.dumps({"error": e.code, "requested": i}) + "\n")
            time.sleep(1)
        got = assemble(out, ep)
        report[ep]["filled"] = len(missing)
        report[ep]["distinct_after_fill"] = len(got)
        print(f"{ep}: {report[ep]}", flush=True)


def main(out, endpoints):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / "harvest.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}
    if endpoints == ["--fill"]:
        fill(out, report)
        report_path.write_text(json.dumps(report, indent=1) + "\n")
        return
    for ep in endpoints:
        print(f"{ep} ...", flush=True)
        report[ep] = harvest(out, ep)
        print(f"{ep}: {report[ep]}", flush=True)
        report_path.write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:] or ENDPOINTS)
