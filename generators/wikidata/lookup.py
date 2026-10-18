"""wikidata in the cascade of the authority datasets (jl.cascade): Wikidata asked online, with the caches of query.py.

resolve: the API's entities (wbgetentities, cached per item in <work>/entities.jsonl.gz): a merged item gives the item
it redirects to, a deleted one None. links: the identity statements as the dataset writes them (best rank, statements
citing JudaicaLink left out: wdtn:P227 GND, P214 VIAF, P244 LC, P1566 GeoNames, P213 ISNI) and the English and German
articles (foaf:isPrimaryTopicOf, the sitelinks). search: the items that state a GND, VIAF, LC, GeoNames or ISNI
number (the Query Service, cached per value in <work>/find-<P>/); an item whose statements of that value all cite
JudaicaLink is left out (0029). write: entities.jsonl.gz of the selected items and find-<P>.tsv of the values searched,
in the formats of query.py (the input of the generator); articles.tsv (header only: the items of Wikipedia articles
come through the dataset dbpedia).
"""

import gzip
import json
import time
from pathlib import Path

from jl import identifiers
from jl.cascade import static_seeds
from urllib.parse import unquote

from jl.generator import load_shared, resolve as resolve_ref
from jl.rdf import Literal, read_triples

q = load_shared("wikidata", "query")      # api, sparql, reduce, FIND, literal, LANGUAGES, SITES
gen = load_shared("wikidata", "generate")  # best, cites_judaicalink, norm_value, article, AS_IRI

WORK = Path("/Users/kai/lokal/judaicalink/work/wikidata-query")
DESCRIBED = "http://data.judaicalink.org/ontology/describedAt"
BHR_PAGES = ("http://steinheim-institut.de:50580/cgi-bin/bhr?id=", "https://www.steinheim-institut.de/cgi-bin/bhr?id=",
             "https://steinheim-institut.de/cgi-bin/bhr?id=", "http://www.steinheim-institut.de/cgi-bin/bhr?id=")
WDTN = "http://www.wikidata.org/prop/direct-normalized/"
TOPIC = "http://xmlns.com/foaf/0.1/isPrimaryTopicOf"
PROP_OF = {"gnd": "P227", "viaf": "P214", "lc-names": "P244", "geonames": "P1566", "isni": "P213"}
SOURCE_OF = {p: s for s, p in PROP_OF.items()}


class Lookup:
    sources = ("wikidata",)
    searched_by = tuple(PROP_OF)

    def __init__(self, cfg, cat, log):
        self.cfg, self.cat, self.log = cfg, cat, log
        WORK.mkdir(parents=True, exist_ok=True)
        self.cache_f = WORK / "entities.jsonl.gz"
        self.cache = {}
        if self.cache_f.exists():
            with gzip.open(self.cache_f, "rt", encoding="utf-8") as g:
                for line in g:
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:   # a line cut off by an interrupted run
                        continue
                    self.cache[row["id"]] = row
        self.searched = {p: set() for p in SOURCE_OF}   # values searched in this cascade, per property
        self.rows = {p: self._find_cache(p) for p in SOURCE_OF}

    # -- the caches ---------------------------------------------------------------------------------
    def entities(self, items):
        """{item: row} as query.entities, asking the API only for items not in the cache."""
        todo = sorted({i for i in items if i not in self.cache})
        for k in range(0, len(todo), 50):
            batch = todo[k:k + 50]
            ans = q.api({"action": "wbgetentities", "ids": "|".join(batch), "props": "labels|claims|sitelinks",
                         "languages": "|".join(q.LANGUAGES), "sitefilter": "|".join(q.SITES)})
            red = {e["redirects"]["from"]: e["redirects"]["to"] for e in ans.get("entities", {}).values()
                   if isinstance(e.get("redirects"), dict)}
            with gzip.open(self.cache_f, "at", encoding="utf-8") as g:
                for i in batch:
                    target = red.get(i, i)
                    e = ans.get("entities", {}).get(target) or ans.get("entities", {}).get(i)
                    row = {"id": i}
                    if target != i:
                        row["redirect"] = target
                    if e and "missing" not in e:
                        row["entity"] = q.reduce(e)
                    g.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                    self.cache[i] = row
            time.sleep(q.PAUSE)
        if todo:
            self.log(f"  wikidata: {len(todo):,} items asked")
        return {i: self.cache[i] for i in items}

    def _find_cache(self, prop):
        d = WORK / f"find-{prop}"
        rows = {}
        for f in ([d / "rows.tsv"] if (d / "rows.tsv").exists() else []) + sorted(d.glob("[0-9]*.tsv")):
            for line in f.read_text(encoding="utf-8").splitlines():
                cells = line.split("\t")
                if len(cells) == 2 and cells[0].startswith('"'):
                    rows.setdefault(cells[0][1:-1], set()).add(line)
        self.asked = getattr(self, "asked", {})
        a = d / "asked.txt"
        self.asked[prop] = set(a.read_text(encoding="utf-8").splitlines()) if a.exists() else set()
        self.asked[prop] |= set(rows)
        return rows

    def find(self, prop, values):
        """{value: {item}}: the items stating the values (Query Service, cached per value)."""
        d = WORK / f"find-{prop}"
        d.mkdir(parents=True, exist_ok=True)
        todo = sorted(v for v in values if v not in self.asked[prop])
        for k in range(0, len(todo), 3000):
            chunk = todo[k:k + 3000]
            answer = q.sparql(q.FIND.format(prop=prop).replace("VALUES_", " ".join(q.literal(v) for v in chunk)))
            new = [line for line in answer.splitlines()[1:] if line]
            with open(d / "rows.tsv", "a", encoding="utf-8") as f:
                f.writelines(line + "\n" for line in new)
            with open(d / "asked.txt", "a", encoding="utf-8") as f:
                f.writelines(v + "\n" for v in chunk)
            for line in new:
                self.rows[prop].setdefault(line.split("\t")[0][1:-1], set()).add(line)
            self.asked[prop].update(chunk)
            time.sleep(q.PAUSE)
        if todo:
            self.log(f"  wikidata: {len(todo):,} values of {prop} asked")
        self.searched[prop].update(values)
        return {v: {line.split("\t")[1].strip("<>").rsplit("/", 1)[-1] for line in self.rows[prop].get(v, ())}
                for v in values}

    # -- the interface ------------------------------------------------------------------------------
    def seeds(self):
        """The static lists, and the items that state the identifier of a record of ours (decision 0029; as
        ls-wikidata matches them): YIVO (P8569, the article name), BHR (P10405, the id of the portal page), Encyclopedia
        of Russian Jewry (P10278, the page id or name of the crawl). All items with these properties are asked once
        from the Query Service (cached); reason by-yivo, by-bhr, by-rujen, detail our record."""
        out = static_seeds(self.cfg, self.cat, "wikidata")
        stable = {slug: self.cat.get(slug).stable for slug in ("yivo", "bhr", "rujen")}
        yw = load_shared("ls-yivo-wikidata", "yivo_wikidata")
        rj = load_shared("rujen", "generate")
        yivo = yw.articles(t for f in resolve_ref(self.cfg, self.cat, f"yivo/{stable['yivo']}")
                           for t in read_triples(f["path"]))
        bhr = {}
        for f in resolve_ref(self.cfg, self.cat, f"bhr/{stable['bhr']}"):
            for s, p, o in read_triples(f["path"]):
                if p == DESCRIBED and not isinstance(o, Literal):
                    for prefix in BHR_PAGES:
                        if str(o).startswith(prefix):
                            bhr.setdefault(str(o)[len(prefix):].lstrip("0"), set()).add(str(s))
        by_id, by_name = {}, {}
        crawl = resolve_ref(self.cfg, self.cat, f"rujen/{stable['rujen']}/rujen.jsonl.gz")[0]["path"]
        with gzip.open(crawl, "rt", encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                if d["title"] != rj.MAIN_PAGE:
                    r = rj.local(d["uri"])
                    by_id[str(d["id"])] = r
                    by_name[unquote(d["uri"]).replace("/index.php/", "").lower()] = r
        rules = {"P8569": ("yivo", lambda v: yivo.get(yw.key(v))),
                 "P10405": ("bhr", lambda v: next(iter(bhr[v.lstrip("0")])) if len(bhr.get(v.lstrip("0"), ())) == 1
                            else None),
                 "P10278": ("rujen", lambda v: by_id.get(v) or by_name.get(v.replace(" ", "_").lower()))}
        for prop, (name, record_of) in rules.items():
            for item, value in self.all_values(prop):
                r = record_of(value)
                if r:
                    out.append(("wikidata", item, f"by-{name}", r))
        return out

    def all_values(self, prop):
        """[(item, value)] of every item with prop (Query Service, cached in the work dir)."""
        path = WORK / f"all-{prop}.tsv"
        if not path.is_file():
            path.write_text(q.sparql(f"SELECT ?item ?v WHERE {{ ?item wdt:{prop} ?v . }}"), encoding="utf-8")
        out = []
        for line in path.read_text(encoding="utf-8").splitlines()[1:]:
            c = line.split("\t")
            if len(c) >= 2:
                out.append((c[0].strip("<>").rsplit("/", 1)[-1], c[1].strip('"').split('"^^')[0]))
        return out

    def resolve(self, source, ids):
        rows = self.entities(ids)
        return {i: (rows[i].get("redirect", i) if "entity" in rows[i] else None) for i in ids}

    def links(self, source, ids):
        rows = self.entities(ids)
        out = {}
        for i in ids:
            e = rows[i].get("entity") or {}
            ls = set()
            for prop, src in SOURCE_OF.items():
                for st in gen.best(e.get("claims", {}).get(prop, [])):
                    x = identifiers.identify(gen.AS_IRI[prop].format(gen.norm_value(prop, st["value"])))
                    if x and x[0] == src:
                        ls.add((WDTN + prop, src, x[1]))
            for wiki in ("enwiki", "dewiki"):
                title = e.get("sitelinks", {}).get(wiki)
                if title:
                    x = identifiers.identify(gen.article(wiki, title))
                    if x:
                        ls.add((TOPIC, x[0], x[1]))
            out[i] = ls
        return out

    def search(self, other_source, ids):
        prop = PROP_OF[other_source]
        values = {gen.norm_value(prop, i): i for i in ids}
        found = self.find(prop, sorted(values))
        items = sorted({x for v in found.values() for x in v if x[:1] == "Q" and x[1:].isdigit()})
        rows = self.entities(items)
        out = {}
        for v, its in found.items():
            for item in its:
                e = (rows.get(item) or {}).get("entity") or {}
                sts = [s for s in e.get("claims", {}).get(prop, []) if gen.norm_value(prop, s.get("value")) == v]
                if sts and all(gen.cites_judaicalink(s) for s in sts):
                    continue   # links to JudaicaLink are never evidence (0029)
                out.setdefault(values[v], set()).add(("wikidata", item))
        return out

    def write(self, out, selection):
        items = sorted(selection.get("wikidata", {}), key=lambda x: (len(x), x))
        rows = self.entities(items)
        with gzip.open(Path(out) / "entities.jsonl.gz", "wt", encoding="utf-8") as g:
            for i in items:
                g.write(json.dumps(rows[i], ensure_ascii=False, sort_keys=True) + "\n")
        for prop in SOURCE_OF:
            lines = sorted(line for v in self.searched[prop] for line in self.rows[prop].get(v, ()))
            (Path(out) / f"find-{prop}.rq").write_text(q.FIND.format(prop=prop), encoding="utf-8")
            with open(Path(out) / f"find-{prop}.tsv", "w", encoding="utf-8") as f:
                f.write("?id\t?item\n")
                f.writelines(line + "\n" for line in lines)
        (Path(out) / "articles.tsv").write_text("title\titem\n", encoding="utf-8")
