"""ls-wikidata: every record of ours that is a Wikidata item, linked to our record of the item (decision 0029).

1. Identity statements: references to Wikidata items (wikidata.org/entity/<Q> in any form, our records
   data/wikidata/<Q>) in our datasets and the other authority datasets (jl.authorities.linking_inputs), resolved
   through the replacements of the dataset wikidata; the rules are in jl.linksets.
2. The identifiers of our sources that Wikidata states (read from the dataset wikidata, current items only):
   - YIVO Encyclopedia (P8569, the article name): the yivo record of the article, matched as in ls-yivo-wikidata
     (yivo_wikidata.key: without case, accents, with spaces, commas and hyphens as underscores);
   - Biographisches Portal der Rabbiner (P10405, the BHR id): the bhr record whose jl:describedAt is the portal page
     of that id (bhr?id=<id>, leading zeros ignored);
   - Encyclopedia of Russian Jewry (P10278, the page id of the wiki, sometimes the page name): the rujen record of
     that page, by the crawl of the stable rujen version and the IRI rule of the rujen generator;
   - the NLI J9U ID (P8189) is not used: our nli-records do not state J9U numbers.
   A record is linked only if the match is unique in both directions: its value leads to one item and that item to
   no other record of the dataset; the others are left out and named in the log.
3. DBpedia through the sitelinks: a dbpedia-persons record data/dbpedia/<name> (the name of the English DBpedia
   resource, which is the title of the English Wikipedia article) and the item whose English Wikipedia article
   (foaf:isPrimaryTopicOf en.wikipedia.org/wiki/<title>) has that title (percent-decoded, underscores as spaces);
   unique in both directions as in 2.
Every link: <record> jl:sameAs <data/wikidata/<Q>>. A link of 2. or 3. that names another item than the record's
identity statements (1.) is left out and listed in the log: a DBpedia name of 2018 can now be the title of another
article (dbpedia/Aaron_Wise, the rabbi, is Q4662552; the article "Aaron Wise" is now Q138545231).
"""

import gzip
import json
from collections import Counter, defaultdict
from urllib.parse import unquote

from jl import authorities
from jl.generator import load_shared
from jl.linksets import JLSAME, authority_index, authority_linkset
from jl.rdf import IRI, Literal

yw = load_shared("ls-yivo-wikidata", "yivo_wikidata")
rujen = load_shared("rujen", "generate")

LINKED = authorities.linking_inputs("wikidata")   # our datasets and the other authority datasets
RUJEN_CRAWL = LINKED["linked_rujen"] + "/rujen.jsonl.gz"
INPUTS = {"authority": authorities.authority_input("wikidata"), **LINKED, "rujen_crawl": RUJEN_CRAWL}
PARAMS = {}

JL = "http://data.judaicalink.org/data/"
PREFIX = JL + "wikidata/"
WDT = "http://www.wikidata.org/prop/direct/"
TOPIC = "http://xmlns.com/foaf/0.1/isPrimaryTopicOf"
DESCRIBED = "http://data.judaicalink.org/ontology/describedAt"
ENWIKI = "https://en.wikipedia.org/wiki/"
BHR_PAGES = ("http://steinheim-institut.de:50580/cgi-bin/bhr?id=", "https://www.steinheim-institut.de/cgi-bin/bhr?id=",
             "http://www.steinheim-institut.de/cgi-bin/bhr?id=")
SOURCES = {"P8569": "yivo", "P10405": "bhr", "P10278": "rujen"}


def title(name):
    return unquote(name).replace("_", " ").strip()


def unique_links(run, kind, values, record_of):
    """values: {item: {value}}; record_of(value) -> record IRI or None. The links unique in both directions."""
    items_of, records_of, unknown = defaultdict(set), defaultdict(set), 0
    for q, vs in values.items():
        for v in vs:
            r = record_of(v)
            if r is None:
                unknown += 1
                run.log(f"{kind}: value names no record: {q} {v}")
                continue
            items_of[r].add(q)
            records_of[q].add(r)
    links, c = {}, Counter()
    for r, qs in sorted(items_of.items()):
        if len(qs) > 1:
            c["left out: several items"] += 1
            run.log(f"{kind}: several items, left out: {r} {', '.join(sorted(qs))}")
            continue
        q = next(iter(qs))
        if len(records_of[q]) > 1:
            c["left out: item of several records"] += 1
            run.log(f"{kind}: item of several records, left out: {q} {', '.join(sorted(records_of[q]))}")
            continue
        links[r] = q
    c["linked"] = len(links)
    c["values naming no record"] = unknown
    return links, c


def generate(run):
    # 1. identity statements
    links = authority_linkset(run, "wikidata", "authority", LINKED, PREFIX)
    by_record = defaultdict(set)
    for s, _p, o in links:
        by_record[str(s)].add(str(o)[len(PREFIX):])
    notes = [run.notes.pop()]   # the counts of authority_linkset

    # what the current items state
    current, _to, _deprecated = authority_index(run, "wikidata", "authority")
    values = {src: defaultdict(set) for src in list(SOURCES) + ["enwiki"]}
    for s, p, o in run.triples("authority"):
        if not str(s).startswith(PREFIX):
            continue
        q = str(s)[len(PREFIX):]
        if q not in current:
            continue
        if p.startswith(WDT) and p[len(WDT):] in SOURCES and isinstance(o, Literal):
            values[p[len(WDT):]][q].add(o.value.strip())
        elif p == TOPIC and str(o).startswith(ENWIKI):
            values["enwiki"][q].add(title(str(o)[len(ENWIKI):]))

    # 2. the identifiers of our sources
    yivo = yw.articles(run.triples("linked_yivo"))
    bhr = {}
    for s, p, o in run.triples("linked_bhr"):
        if p == DESCRIBED and not isinstance(o, Literal):
            for prefix in BHR_PAGES:
                if str(o).startswith(prefix):
                    bhr.setdefault(str(o)[len(prefix):].lstrip("0"), set()).add(str(s))
    by_id, by_name = {}, {}
    with gzip.open(run.input("rujen_crawl"), "rt", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d["title"] == rujen.MAIN_PAGE:
                continue
            r = rujen.local(d["uri"])
            by_id[str(d["id"])] = r
            by_name[unquote(d["uri"]).replace("/index.php/", "").lower()] = r
    rujen_records = {str(s) for s, _p, _o in run.triples("linked_rujen")}
    dbpedia = {}
    for s, _p, _o in run.triples("linked_dbpedia_persons"):
        s = str(s)
        if s.startswith(JL + "dbpedia/"):
            dbpedia.setdefault(title(s[len(JL + "dbpedia/"):]), set()).add(s)

    def one(found):
        return next(iter(found)) if found and len(found) == 1 else None

    def rujen_of(v):
        r = by_id.get(v) or by_name.get(v.replace(" ", "_").lower())
        return r if r in rujen_records else None

    rules = {"P8569": ("yivo (P8569)", lambda v: yivo.get(yw.key(v))),
             "P10405": ("bhr (P10405)", lambda v: one(bhr.get(v.lstrip("0")))),
             "P10278": ("rujen (P10278)", rujen_of),
             "enwiki": ("dbpedia-persons (English Wikipedia)", lambda v: one(dbpedia.get(v)))}
    t = set(links)
    for key_, (kind, record_of) in rules.items():
        found, c = unique_links(run, kind, values[key_], record_of)
        new = 0
        for r, q in found.items():
            if by_record.get(r) and q not in by_record[r]:
                run.log(f"{kind}: another item than the identity statements, left out: {r} {q} (identity: "
                        f"{', '.join(sorted(by_record[r]))})")
                c["left out: another item than the identity statements"] += 1
                continue
            if (IRI(r), IRI(JLSAME), IRI(PREFIX + q)) not in t:
                new += 1
            t.add((IRI(r), IRI(JLSAME), IRI(PREFIX + q)))
        c["new links"] = new
        notes.append(f"{kind}: " + ", ".join(f"{k} {v:,}" for k, v in sorted(c.items())))
    run.notes.extend(notes)
    run.note(f"{len(t):,} links in all.")
    run.write_turtle("ls-wikidata.ttl.gz", t)
