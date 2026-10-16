"""Find the GeoNames ids of the Footprints places and have Footprints confirm them (input of the generator).

python3 geonames.py <harvest dir> <allCountries.zip>

Footprints makes every place from a GeoNames record (name, region and country as the canonical name, the
coordinates copied), but its API does not give the GeoNames id. Candidates come from the GeoNames dump: records whose
name (or ASCII or alternate name) is the first part of the canonical name, within 30 km; ranked by equal
coordinates, feature class (populated places and areas first) and distance. Each candidate is tried at
/api/altname/?geonameId=<id>, which lists the place names of the place that has that GeoNames id; the first
candidate whose answer names our place is confirmed. Writes geonames/altname/<geonames id>.json (the answers,
unchanged) and geonames/places.tsv (place id, canonical name, GeoNames id or empty, how: confirmed or the reason
none was found, candidates tried). One request per second, at most MAX_TRIES per place.
"""

import csv
import gzip
import io
import json
import math
import sys
import time
import unicodedata
import urllib.error
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from jl.fetch import get  # noqa: E402

API = "https://footprints.ctl.columbia.edu/api/altname/?format=json&geonameId="
RADIUS_KM = 30
MAX_TRIES = 5
CLASS_RANK = {"P": 0, "A": 1}


def norm(s):
    s = unicodedata.normalize("NFKD", s.casefold())
    return "".join(c for c in s if not unicodedata.combining(c)).strip()


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def places(harvest):
    """The canonical places named anywhere in the harvest: id -> (name, lat, lng)."""
    found = {}

    def take(p):   # a place with its canonical place, or (the place endpoint) a canonical place
        cp = p.get("canonical_place") if p and "canonical_place" in p else p
        if cp and cp.get("id") is not None and cp.get("latitude") is not None:
            found[cp["id"]] = (cp["canonical_name"], float(cp["latitude"]), float(cp["longitude"]))

    for ep in ["imprint", "book", "footprint", "place"]:
        path = harvest / f"{ep}.jsonl.gz"
        if not path.exists():
            continue
        for line in gzip.open(path, "rt", encoding="utf-8"):
            r = json.loads(line)
            if ep == "place":
                take(r)
            elif ep == "book":
                take((r.get("imprint") or {}).get("place"))
            else:
                take(r.get("place"))
    return found


def candidates(found, dump):
    """place id -> [(rank, geonames id, name, distance)], from the GeoNames dump."""
    cells = {}
    for pid, (name, lat, lng) in found.items():
        cells.setdefault((math.floor(lat), math.floor(lng)), []).append(pid)
    want = {pid: norm(name.split(",")[0]) for pid, (name, _, _) in found.items()}
    out = {pid: [] for pid in found}
    with zipfile.ZipFile(dump) as z:
        with z.open("allCountries.txt") as f:
            for row in io.TextIOWrapper(f, encoding="utf-8"):
                c = row.split("\t")
                lat, lng = float(c[4]), float(c[5])
                near = []
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        near.extend(cells.get((math.floor(lat) + dy, math.floor(lng) + dx), ()))
                if not near:
                    continue
                names = None
                for pid in near:
                    _, plat, plng = found[pid]
                    d = km((lat, lng), (plat, plng))
                    if d > RADIUS_KM:
                        continue
                    if names is None:
                        names = {norm(c[1]), norm(c[2])} | {norm(a) for a in c[3].split(",") if a}
                    if want[pid] not in names:
                        continue
                    same = (lat, lng) == (plat, plng)
                    out[pid].append(((0 if same else 1, CLASS_RANK.get(c[6], 2), d), c[0], c[1], round(d, 2)))
    for pid in out:
        out[pid].sort()
    return out


def confirm(gid, pid, cache):
    path = cache / f"{gid}.json"
    if not path.exists():
        try:
            body = get(API + gid)
        except urllib.error.HTTPError as e:
            body = json.dumps({"error": e.code}).encode()
        path.write_bytes(body)
        time.sleep(1)
    data = json.loads(path.read_bytes())
    return any((r.get("canonical_place") or {}).get("id") == pid for r in data.get("results", []))


def main(harvest, dump):
    harvest = Path(harvest)
    out = harvest / "geonames"
    cache = out / "altname"
    cache.mkdir(parents=True, exist_ok=True)
    found = places(harvest)
    print(f"{len(found)} places; reading the GeoNames dump ...", flush=True)
    cands = candidates(found, dump)
    rows, n = [], 0
    for pid in sorted(found):
        name = found[pid][0]
        tried, gid, how = [], "", "no candidate"
        for _, cg, cname, d in cands[pid][:MAX_TRIES]:
            tried.append(f"{cg} {cname} {d}km")
            if confirm(cg, pid, cache):
                gid, how = cg, "confirmed"
                break
            how = "not confirmed"
        rows.append([pid, name, gid, how, "; ".join(tried)])
        n += 1
        if n % 50 == 0:
            print(f"  {n} of {len(found)}", flush=True)
    with open(out / "places.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["place", "canonical_name", "geonames", "how", "tried"])
        w.writerows(rows)
    hows = {}
    for r in rows:
        hows[r[3]] = hows.get(r[3], 0) + 1
    print(hows, flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
