"""Ask Wikidata for the items of the GeoNames ids and GND numbers of the geo-coordinates places (generator input).

python3 fetch_wikidata.py <geo-coordinates file (.ttl.gz)> <out dir>

Writes, for the input web-caches/wikidata-geonames-<date>:
- p1566.rq, p1566.tsv: the items with a GeoNames ID (P1566) among the GeoNames ids of the places;
- p227.rq, p227.tsv: the items with a GND ID (P227) among the GND numbers of the places;
- sitelinks.rq, sitelinks.tsv: the English, German and Russian Wikipedia articles of all items found.
The .rq files are the query templates (VALUES filled in batches of BATCH); the .tsv files are the answers of the
Wikidata Query Service, one header line, the rows of all batches sorted. One request per second; the User-Agent is
the framework's (decision 0028).
"""

import re
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from jl.fetch import get  # noqa: E402
from jl.rdf import read_triples  # noqa: E402

ENDPOINT = "https://query.wikidata.org/sparql?query="
BATCH = 300
QUERIES = {
    "p1566": "SELECT ?id ?item WHERE { VALUES ?id { %s } ?item wdt:P1566 ?id . }",
    "p227": "SELECT ?id ?item WHERE { VALUES ?id { %s } ?item wdt:P227 ?id . }",
    "sitelinks": ("SELECT ?item ?article WHERE { VALUES ?item { %s } ?article schema:about ?item ; "
                  "schema:isPartOf ?wiki . VALUES ?wiki { <https://en.wikipedia.org/> <https://de.wikipedia.org/> "
                  "<https://ru.wikipedia.org/> } }"),
}


def ask(name, values, out):
    rows, header = set(), None
    values = sorted(values)
    for i in range(0, len(values), BATCH):
        q = QUERIES[name] % " ".join(values[i:i + BATCH])
        body = get(ENDPOINT + urllib.parse.quote(q), headers={"Accept": "text/tab-separated-values"}).decode("utf-8")
        lines = body.rstrip("\n").split("\n")
        header = lines[0]
        rows.update(lines[1:])
        print(f"  {name}: {min(i + BATCH, len(values))} of {len(values)}, {len(rows)} rows", flush=True)
        time.sleep(1)
    (out / f"{name}.rq").write_text(QUERIES[name].replace("%s", "…") + "\n", encoding="utf-8")
    (out / f"{name}.tsv").write_text("\n".join([header, *sorted(rows)]) + "\n", encoding="utf-8")
    return rows


def main(places, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    geonames, gnd = set(), set()
    for s, p, o in read_triples(places):
        m = re.match(r"^https?://(?:sws\.)?geonames\.org/([0-9]+)/?$", str(o))
        if m:
            geonames.add(f'"{m.group(1)}"')
        m = re.match(r"^https?://d-nb\.info/gnd/([0-9]+[0-9X-]*)$", str(o))
        if m:
            gnd.add(f'"{m.group(1)}"')
    items = set()
    for name, values in (("p1566", geonames), ("p227", gnd)):
        for row in ask(name, values, out):
            items.add("wd:" + row.split("\t")[1].strip("<>").rsplit("/", 1)[1])
    ask("sitelinks", items, out)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
