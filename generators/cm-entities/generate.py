"""cm-entities: what is known about the entities that TagMe linked in Compact Memory (cm-tagme).

Transformation only, a port of cm_entities_presence (kg-complements datasets_deterministic.py) and
cm_entities_wikidata (datasets_algorithmic.py), 2026-10-05/06, without changes to their logic (decision 0020):

- cm-entities-presence.ttl.gz: for every entity a jl:CorpusPresence in the corpus Compact Memory (decided 2026-10-12:
  no corpus in the term names): the number of mentions and pages, first and last year, number of journals and the
  journal with the most mentions (years and journals from the full-text bundle, via the page VLID). The node IRI is
  data/cm-entities/presence/<the entity IRI after data/>.
- cm-entities-wikidata.ttl.gz: for the entities that no dataset names, the Wikidata item (via the German Wikipedia
  title in the entity IRI, following redirects), labels in German, English and Hebrew, type (person, or place if the
  item has coordinates), coordinates, and GND, VIAF and GeoNames IDs.

"No dataset names" was checked in 2021/2026 against the whole endpoint; here against the versions that name any of
these entities: dbpedia-persons and interlinks (checked 2026-10-12 against all stable versions of the catalogue: no
other version names one of them). The API answers come from the cache of 2026-10-06; an answer missing there is an
error, never a live request (acquisition is a separate step, decision 0018).
"""

import gzip
import hashlib
import json
from collections import Counter, defaultdict
from urllib.parse import unquote

from jl.generator import GeneratorError
from jl.rdf import IRI, RDF_TYPE, XSD, Literal
from jl.turtle import PREFIXES

INPUTS = {
    "tagme": "cm-tagme/2021-01-18",
    "fulltext": "inputs:compact-memory/fulltext-2026-10-05-v2/",
    "cache": "inputs:web-caches/api-cache-2026-10-06/",
    "dbpedia_persons": "dbpedia-persons/2018-10-24",
    "interlinks": "interlinks/2018-07-18",
}
PARAMS = {}

JLO = PREFIXES["jl"]
OWL = PREFIXES["owl"]
FOAF = PREFIXES["foaf"]
SKOS = PREFIXES["skos"]
RDFS = PREFIXES["rdfs"]
GEO = PREFIXES["geosparql"]
CM = "http://data.judaicalink.org/data/compact-memory/"
CORPUS = CM + "corpus"
DATA = "http://data.judaicalink.org/data/"
PRESENCE = DATA + "cm-entities/presence/"
WIKIPEDIA_API = "https://de.wikipedia.org/w/api.php"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
NAMES = {SKOS + "prefLabel", FOAF + "name", RDFS + "label"}


def integer(n):
    return Literal(str(n), XSD + "integer")


def chunks(items, n):
    items = list(items)
    for i in range(0, len(items), n):
        yield items[i:i + n]


class Cache:
    """The API answers of 2026-10-06, by the sha1 of the request (as kg-complements stored them)."""

    def __init__(self, paths):
        self.files = {p.name: p for p in paths}
        self.used = 0

    def get(self, url, params):
        key = hashlib.sha1((url + "?" + json.dumps(params, sort_keys=True)).encode()).hexdigest()
        p = self.files.get(f"{key}.json")
        if p is None:
            raise GeneratorError(f"no cached answer for {url} {params} (an acquisition step would have to query it)")
        self.used += 1
        return json.loads(p.read_text())


def bundle_pages(run):
    files = {p.name: p for p in run.inputs("fulltext")}
    manifest = json.loads(files["manifest.json"].read_text(encoding="utf-8"))
    out = {}
    for part in manifest["parts"]:
        with gzip.open(files[part["file"]], "rt", encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                out[d["id"]] = (d.get("dateIssued"), d["vlid_journal"])
    return out


def presence(run, refs, ref_page, bundle):
    """Mentions, pages, years and journals per entity (the SPARQL join ?e hasReference ?r . ?r isOnPage ?pg)."""
    per_page = Counter()
    for e, r in refs:
        for pg in ref_page.get(r, ()):
            per_page[(e, pg)] += 1
    agg = defaultdict(lambda: {"mentions": 0, "pages": 0, "years": [], "journals": Counter()})
    for (e, pg), n in per_page.items():
        a = agg[e]
        a["mentions"] += n
        a["pages"] += 1
        hit = bundle.get(pg.rsplit("-", 1)[-1])
        if hit:
            date, journal = hit
            if date:
                a["years"].append(int(date[:4]))
            a["journals"][journal] += n
    t = []
    for x, a in agg.items():
        if not x.startswith(DATA):
            raise GeneratorError(f"entity outside data/: {x}")
        s = IRI(PRESENCE + x[len(DATA):])
        t += [(s, IRI(RDF_TYPE), IRI(JLO + "CorpusPresence")), (s, IRI(JLO + "entity"), IRI(x)),
              (s, IRI(JLO + "corpus"), IRI(CORPUS)),
              (s, IRI(JLO + "mentionCount"), integer(a["mentions"])), (s, IRI(JLO + "pageCount"), integer(a["pages"]))]
        if a["years"]:
            t += [(s, IRI(JLO + "firstMentionYear"), Literal(str(min(a["years"])), XSD + "gYear")),
                  (s, IRI(JLO + "lastMentionYear"), Literal(str(max(a["years"])), XSD + "gYear"))]
        if a["journals"]:
            t.append((s, IRI(JLO + "journalCount"), integer(len(a["journals"]))))
            # most mentions; ties by journal id, so that the result is deterministic
            top = sorted(a["journals"].items(), key=lambda kv: (-kv[1], int(kv[0]) if kv[0].isdigit() else 0, kv[0]))[0][0]
            t.append((s, IRI(JLO + "mostFrequentJournal"), IRI(CM + top)))
    run.note(f"Presence: {len(agg):,} entities.")
    return t


def claims(entity, prop):
    out = []
    for c in entity.get("claims", {}).get(prop, []):
        v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
        if v is not None:
            out.append(v)
    return out


def wikidata(run, entities, cache):
    title_of = {e: unquote(e.rsplit("/", 1)[-1]).replace("_", " ") for e in entities}
    # 1. German Wikipedia title -> Wikidata item (follows redirects and normalisation)
    qid_of_title = {}
    for batch in chunks(sorted(set(title_of.values())), 50):
        data = cache.get(WIKIPEDIA_API, {"action": "query", "titles": "|".join(batch), "prop": "pageprops",
                                         "ppprop": "wikibase_item", "redirects": 1, "format": "json"})
        q = (data or {}).get("query", {})
        back = {t_: t_ for t_ in batch}
        for n in q.get("normalized", []):
            back[n["to"]] = back.get(n["from"], n["from"])
        for rd in q.get("redirects", []):
            back[rd["to"]] = back.get(rd["from"], rd["from"])
        for page in q.get("pages", {}).values():
            qid = page.get("pageprops", {}).get("wikibase_item")
            if qid and page.get("title") in back:
                qid_of_title[back[page["title"]]] = qid
    # 2. Wikidata items
    items = {}
    for batch in chunks(sorted(set(qid_of_title.values())), 50):
        data = cache.get(WIKIDATA_API, {"action": "wbgetentities", "ids": "|".join(batch), "props": "labels|claims",
                                        "languages": "de|en|he", "format": "json"})
        items.update((data or {}).get("entities", {}))
    t = []
    kinds = Counter()
    for x, title in sorted(title_of.items()):
        qid = qid_of_title.get(title)
        item = items.get(qid) if qid else None
        if not item or "missing" in item:
            kinds["no Wikidata item"] += 1
            continue
        s = IRI(x)
        t += [(s, IRI(OWL + "sameAs"), IRI(f"http://www.wikidata.org/entity/{qid}")),
              (s, IRI(FOAF + "isPrimaryTopicOf"), IRI("https://de.wikipedia.org/wiki/" + title.replace(" ", "_")))]
        for lang in ("de", "en", "he"):
            label = item.get("labels", {}).get(lang, {}).get("value")
            if label:
                t.append((s, IRI(SKOS + "prefLabel"), Literal(label, lang=lang)))
        instance_of = {v.get("id") for v in claims(item, "P31") if isinstance(v, dict)}
        coords = claims(item, "P625")
        if "Q5" in instance_of:
            t.append((s, IRI(RDF_TYPE), IRI(FOAF + "Person"))); kinds["person"] += 1
        elif coords:
            t.append((s, IRI(RDF_TYPE), IRI(JLO + "Place"))); kinds["place"] += 1
        else:
            kinds["other"] += 1
        if coords:
            c = coords[0]
            t.append((s, IRI(GEO + "asWKT"), Literal(f"POINT({c['longitude']} {c['latitude']})", GEO + "wktLiteral")))
        for v in claims(item, "P227"):
            t.append((s, IRI(OWL + "sameAs"), IRI(f"http://d-nb.info/gnd/{v}")))
        for v in claims(item, "P214"):
            t.append((s, IRI(OWL + "sameAs"), IRI(f"http://viaf.org/viaf/{v}")))
        for v in claims(item, "P1566"):
            t.append((s, IRI(OWL + "sameAs"), IRI(f"http://sws.geonames.org/{v}/")))
    run.note(f"Wikidata: {len(title_of):,} entities not named by any dataset; {dict(sorted(kinds.items()))}; "
             f"{cache.used:,} cached API answers used.")
    return t


def generate(run):
    refs, ref_page = [], defaultdict(list)
    for s, p, o in run.triples("tagme"):
        if p == JLO + "hasReference":
            refs.append((str(s), str(o)))
        elif p == JLO + "isOnPage":
            ref_page[str(s)].append(str(o))
    entities = {e for e, _r in refs}
    run.log(f"cm-tagme: {len(refs):,} references of {len(entities):,} entities")
    named = set()
    for name in ("dbpedia_persons", "interlinks"):
        found = {str(s) for s, p, o in run.triples(name) if str(s) in entities and p in NAMES}
        run.log(f"named in {name}: {len(found):,}")
        named |= found
    run.write_turtle("cm-entities-presence.ttl.gz", presence(run, refs, ref_page, bundle_pages(run)))
    run.write_turtle("cm-entities-wikidata.ttl.gz",
                     wikidata(run, sorted(entities - named), Cache(run.inputs("cache"))))
