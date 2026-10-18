"""Ask Wikidata for the items our data reaches and their content (makes the input of wikidata).

python3 query.py <out dir> [<work dir>] [--use <slug>/<version or run id> …]

--use: read this version or run instead of the stable version (as jl generate --use; a round of the authority
datasets, jl.authorities).

1. The identifiers our data names (ids.py: the stable versions and the runs named there).
2. Which items:
   - the items named;
   - the items that state one of the identifiers: the Wikidata Query Service, find-<P>.rq/.tsv (P227 GND, P214 VIAF,
     P244 LC, P1566 GeoNames, P213 ISNI), one query per batch of values;
   - the items of the English Wikipedia articles of DBpedia resources: the Wikidata API (wbgetentities with
     sites=enwiki and titles), articles.tsv (title, item).
3. Their content: the Wikidata API (wbgetentities, 50 items per request; it follows redirects of merged items):
   entities.jsonl.gz, one line per requested item: {"id": requested id, "redirect": the item it redirects to (if
   merged), "entity": the entity as the API gives it, reduced to the labels (en, de, he, mul), the sitelinks (enwiki,
   dewiki, hewiki) and the statements of the properties PROPS (rank, value, and of the references only P248 stated
   in, P143 imported from, P854 reference URL)}. Never P13183 or other JudaicaLink properties.
Batches are kept in the work dir, so an interrupted run continues. One request at a time, a pause between requests,
waiting longer on 429/503 and on the API's maxlag answer.
"""

import gzip
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from jl import catalog, config, generator  # noqa: E402
from jl.fetch import request  # noqa: E402
from jl.rdf import read_triples  # noqa: E402

ids = None   # ids.py, imported by load_ids() after --use is set (its DATASETS are evaluated on import)


def parse_args(argv):
    args, use = [], []
    it = iter(argv)
    for a in it:
        if a == "--use":
            use.append(next(it, ""))
        else:
            args.append(a)
    return args, use


def load_ids(use):
    global ids
    generator.USE.update(generator.parse_use(use))   # read by ids.DATASETS (jl.authorities.linking_inputs)
    import ids as module  # noqa: E402
    ids = module

WDQS = "https://query.wikidata.org/sparql"
API = "https://www.wikidata.org/w/api.php"
PAUSE = 1
PROPS = ["P31", "P19", "P20", "P569", "P570", "P227", "P214", "P244", "P1566", "P213", "P8189", "P8569", "P10405",
         "P10278"]
REF_PROPS = {"P248", "P143", "P854"}
LANGUAGES = ["en", "de", "he", "mul"]
SITES = ["enwiki", "dewiki", "hewiki"]
FIND = "SELECT ?id ?item WHERE {{ VALUES ?id {{ VALUES_ }} ?item wdt:{prop} ?id . }}\n"
stats = {"wdqs": 0, "api": 0, "waits": 0}


def wait_for(i, e=None):
    wait = 0
    if isinstance(e, urllib.error.HTTPError):
        wait = int(e.headers.get("Retry-After") or 0)
    wait = wait or 20 * (i + 1)
    stats["waits"] += 1
    print(f"  waiting {wait} s ({e})", flush=True)
    time.sleep(wait)


def sparql(query):
    data = urllib.parse.urlencode({"query": query}).encode()
    for i in range(8):
        try:
            req = request(WDQS, data=data, headers={"Accept": "text/tab-separated-values",
                                                    "Content-Type": "application/x-www-form-urlencoded"})
            stats["wdqs"] += 1
            with urllib.request.urlopen(req, timeout=120) as r:
                text = r.read().decode("utf-8")
            lines = text.splitlines()
            n = len(lines[0].split("\t")) if lines else 0
            if n and all(len(line.split("\t")) == n for line in lines):
                return text
            # the service stopped in the middle of its answer (status 200, its error text appended)
            wait_for(i, "incomplete answer")
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504):
                raise
            wait_for(i, e)
        except Exception as e:   # time-outs, connection resets
            wait_for(i, e)
    raise RuntimeError("the query service did not answer")


def api(params):
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json", "maxlag": "10"})
    for i in range(360):   # up to an hour of replication lag
        try:
            stats["api"] += 1
            with urllib.request.urlopen(request(url), timeout=120) as r:
                d = json.loads(r.read())
            if d.get("error", {}).get("code") == "maxlag":   # the database replicas lag: wait and ask again
                stats["waits"] += 1
                time.sleep(10)
                continue
            if "error" in d:
                raise RuntimeError(f"API error: {d['error']}")
            return d
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504):
                raise
            wait_for(i, e)
        except (TimeoutError, ConnectionError, urllib.error.URLError) as e:
            wait_for(i, e)
    raise RuntimeError("the API did not answer")


def literal(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def find(prop, values, out, work):
    """WDQS: the items that state the values; writes find-<prop>.rq and .tsv (the rows of the values, as the service
    answers them). The work dir keeps, per value asked, the answer rows (asked.txt, rows.tsv), so that a changed list
    of values asks only for the new ones; batch files of an earlier layout (<n>.tsv) are read as answers too."""
    template = FIND.format(prop=prop)
    d = work / f"find-{prop}"
    d.mkdir(parents=True, exist_ok=True)
    asked_f, rows_f = d / "asked.txt", d / "rows.tsv"
    asked = set(asked_f.read_text(encoding="utf-8").splitlines()) if asked_f.exists() else set()
    rows = {}   # value -> set of raw lines
    sources = [rows_f] if rows_f.exists() else []
    sources += sorted(d.glob("[0-9]*.tsv"))
    for f in sources:
        for line in f.read_text(encoding="utf-8").splitlines():
            cells = line.split("\t")
            if len(cells) == 2 and cells[0].startswith('"'):
                v = cells[0][1:-1]
                rows.setdefault(v, set()).add(line)
                asked.add(v)
    todo = [v for v in values if v not in asked]
    print(f"find-{prop}: {len(values):,} values, {len(todo):,} to ask", flush=True)
    size = 3000
    for i in range(0, len(todo), size):
        chunk = todo[i:i + size]
        answer = sparql(template.replace("VALUES_", " ".join(literal(v) for v in chunk)))
        new = [line for line in answer.splitlines()[1:] if line]
        with open(rows_f, "a", encoding="utf-8") as f:
            f.writelines(line + "\n" for line in new)
        with open(asked_f, "a", encoding="utf-8") as f:
            f.writelines(v + "\n" for v in chunk)
        for line in new:
            rows.setdefault(line.split("\t")[0][1:-1], set()).add(line)
        print(f"find-{prop}: {min(i + size, len(todo)):,} of {len(todo):,} asked", flush=True)
        time.sleep(PAUSE)
    lines = sorted(line for v in values for line in rows.get(v, ()))
    (out / f"find-{prop}.rq").write_text(template, encoding="utf-8")
    with open(out / f"find-{prop}.tsv", "w", encoding="utf-8") as f:
        f.write("?id\t?item\n")
        f.writelines(line + "\n" for line in lines)
    print(f"find-{prop}: {len(lines):,} rows", flush=True)
    return {line.split("\t")[1].strip("<>").rsplit("/", 1)[-1] for line in lines}


def articles(names, out, work):
    """API: the items of English Wikipedia articles (titles); writes articles.tsv (title, item). The work dir keeps
    the answer per title asked (articles.jsonl), so that only new titles are asked."""
    cache_f = work / "articles.jsonl"
    cache = {}
    if cache_f.exists():
        for line in cache_f.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            cache[r["title"]] = r["item"]
    todo = [n for n in names if n not in cache]
    print(f"articles: {len(names):,} titles, {len(todo):,} to ask", flush=True)
    for i in range(0, len(todo), 50):
        chunk = todo[i:i + 50]
        ans = api({"action": "wbgetentities", "sites": "enwiki", "titles": "|".join(chunk), "props": "sitelinks",
                   "sitefilter": "enwiki"})
        got = {}
        for qid, e in ans.get("entities", {}).items():
            title = e.get("sitelinks", {}).get("enwiki", {}).get("title")
            if qid.startswith("Q") and title:
                got[title] = qid
        with open(cache_f, "a", encoding="utf-8") as f:
            for n in chunk:
                f.write(json.dumps({"title": n, "item": got.get(n)}, ensure_ascii=False) + "\n")
                cache[n] = got.get(n)
        if (i // 50) % 20 == 0:
            print(f"articles: {min(i + 50, len(todo)):,} of {len(todo):,} asked", flush=True)
        time.sleep(PAUSE)
    pairs = sorted((n, cache[n]) for n in names if cache.get(n))
    with open(out / "articles.tsv", "w", encoding="utf-8") as f:
        f.write("title\titem\n")
        f.writelines(f"{t}\t{q}\n" for t, q in pairs)
    return {q for _t, q in pairs}


def reduce(e):
    claims = {}
    for p in PROPS:
        out = []
        for st in e.get("claims", {}).get(p, []):
            refs = [{rp: [s.get("datavalue", {}).get("value") for s in snaks]
                     for rp, snaks in r.get("snaks", {}).items() if rp in REF_PROPS}
                    for r in st.get("references", [])]
            out.append({"rank": st.get("rank"), "value": st.get("mainsnak", {}).get("datavalue", {}).get("value"),
                        "references": [r for r in refs if r]})
        if out:
            claims[p] = out
    return {"id": e.get("id"), "labels": {k: v["value"] for k, v in e.get("labels", {}).items() if k in LANGUAGES},
            "sitelinks": {k: v["title"] for k, v in e.get("sitelinks", {}).items() if k in SITES},
            "claims": claims}


def entities(items, out, work):
    """API: the content of the items; writes entities.jsonl.gz. The work dir keeps the answer per item asked
    (entities.jsonl.gz, appended), so that only new items are asked."""
    cache_f = work / "entities.jsonl.gz"
    cache = {}
    if cache_f.exists():
        with gzip.open(cache_f, "rt", encoding="utf-8") as g:
            for line in g:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:   # a line cut off by an interrupted run
                    continue
                cache[row["id"]] = row
    todo = [q for q in items if q not in cache]
    print(f"entities: {len(items):,} items, {len(todo):,} to ask", flush=True)
    for i in range(0, len(todo), 50):
        batch = todo[i:i + 50]
        ans = api({"action": "wbgetentities", "ids": "|".join(batch), "props": "labels|claims|sitelinks",
                   "languages": "|".join(LANGUAGES), "sitefilter": "|".join(SITES)})
        red = {e["redirects"]["from"]: e["redirects"]["to"] for e in ans.get("entities", {}).values()
               if isinstance(e.get("redirects"), dict)}
        with gzip.open(cache_f, "at", encoding="utf-8") as g:
            for q in batch:
                target = red.get(q, q)
                e = ans.get("entities", {}).get(target) or ans.get("entities", {}).get(q)
                row = {"id": q}
                if target != q:
                    row["redirect"] = target
                if e and "missing" not in e:
                    row["entity"] = reduce(e)
                g.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                cache[q] = row
        if (i // 50) % 100 == 0:
            print(f"entities: {min(i + 50, len(todo)):,} of {len(todo):,} asked", flush=True)
        time.sleep(PAUSE)
    with gzip.open(out / "entities.jsonl.gz", "wt", encoding="utf-8") as g:
        for q in items:
            g.write(json.dumps(cache[q], ensure_ascii=False, sort_keys=True) + "\n")
    return {q: cache[q] for q in items}


def main(out, work):
    out, work = Path(out), Path(work)
    out.mkdir(parents=True, exist_ok=True)
    cfg, cat, t0 = config.load(), catalog.Catalog(), time.time()

    def triples_of():
        for _name, ref in ids.DATASETS.items():
            for f in generator.resolve(cfg, cat, ref):
                if generator.is_meta(f["file"]) or not f["file"].endswith((".ttl.gz", ".nt.gz", ".ttl", ".nt")):
                    continue
                yield ref.split("/", 1)[0], read_triples(f["path"])
    found = ids.collect(triples_of())
    print({k: len(v) for k, v in found.items()}, flush=True)

    items = set(found["wikidata"])
    for source, prop in ids.PROPERTIES.items():
        values = sorted(found[source])
        if source == "isni":
            values = [ids.isni_value(v) for v in values if len(v) == 16]
        items |= find(prop, values, out, work)
    items |= articles(sorted({ids.article_name(n) for n in found["dbpedia"]}), out, work)
    items = sorted((i for i in items if i[:1] == "Q" and i[1:].isdigit()), key=lambda x: int(x[1:]))
    print(f"{len(items):,} items", flush=True)
    rows = entities(items, out, work)
    # items that the named ones were merged into and that were not asked for themselves
    extra = sorted({r["redirect"] for r in rows.values() if "redirect" in r} - set(items), key=lambda x: int(x[1:]))
    print(f"{len(extra)} redirect targets (included in the answers of their old ids)", flush=True)
    print(f"done: {stats['wdqs']} queries, {stats['api']} API requests, {stats['waits']} waits, "
          f"{round(time.time() - t0)} s", flush=True)


if __name__ == "__main__":
    ARGS, USE = parse_args(sys.argv[1:])
    if len(ARGS) not in (1, 2):
        sys.exit(__doc__)
    load_ids(USE)
    print("datasets:", ", ".join(sorted(ids.DATASETS.values())), flush=True)
    main(ARGS[0], ARGS[1] if len(ARGS) == 2 else "/Users/kai/lokal/judaicalink/work/wikidata-query")
