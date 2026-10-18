"""dbpedia: the English and German Wikipedia articles (DBpedia resources) JudaicaLink uses (decisions 0029, 0031).

Per language one source: the article https://<lang>.wikipedia.org/wiki/<title> and the resource
http://dbpedia.org/resource/<title> (en) or http://de.dbpedia.org/resource/<title> (de) are one identifier.

1. The selection list (dbpedia-selection.tsv.gz): one row per source (wikipedia-en, wikipedia-de), title and dataset
   that names it (our datasets with every statement, the other authority datasets with their declared identity
   statements: jl.authorities.linking_inputs; and the records of dbpedia-persons, which this dataset replaces), with
   the current title (empty if the article does not exist). Titles in other namespaces than articles are not
   selected (query.py).
2. The data (dbpedia.ttl.gz), per language and current article, a record data/dbpedia/<lang>/<title> (the title
   escaped where an IRI needs it, jl.identifiers.title_iri_part): owl:sameAs the DBpedia resource and the Wikidata
   item of the article (from Wikipedia's page properties), foaf:isPrimaryTopicOf the article, skos:prefLabel the
   title (with spaces, in the language of the article).
3. The records of dbpedia-persons (data/dbpedia/<name>, from the English DBpedia where the name is an English
   article, else the German one): their statements go to the record of the current article, and
   data/dbpedia/<name> dcterms:isReplacedBy that record (owl:deprecated true if the article no longer exists).
4. Redirects (decision 0031, as GND numbers in 0029): a title that redirects, <resource of the old title>
   dcterms:isReplacedBy <resource of the current one>, and the same for the articles; a title that does not exist
   (any more), <resource> owl:deprecated true.
"""

import csv
import gzip
import json

from jl import authorities, identifiers
from jl.generator import load_shared
from jl.iris import canonical, canonical_triples
from jl.rdf import IRI, Literal
from jl.turtle import PREFIXES

q = load_shared("dbpedia", "query")   # is_article, LANGS

CACHE = "inputs:web-caches/dbpedia-2026-10-18/"
LINKED = authorities.linking_inputs("dbpedia")   # our datasets and the other authority datasets
INPUTS = {"titles_en": CACHE + "titles-en.jsonl", "titles_de": CACHE + "titles-de.jsonl",
          "previous": "dbpedia-persons/2018-10-24", **LINKED}
PARAMS = {}

JL = "http://data.judaicalink.org/data/"
OLD = JL + "dbpedia/"
OWL, SKOS, FOAF, DCT, XSD = (PREFIXES[p] for p in ("owl", "skos", "foaf", "dcterms", "xsd"))
SAME, REPLACED, DEPRECATED = OWL + "sameAs", DCT + "isReplacedBy", OWL + "deprecated"
RESOURCE = {"en": "http://dbpedia.org/resource/", "de": "http://de.dbpedia.org/resource/"}
ARTICLE = {"en": "https://en.wikipedia.org/wiki/", "de": "https://de.wikipedia.org/wiki/"}
WD = "http://www.wikidata.org/entity/"


def answers(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            out[r["asked"]] = r
    return out


def generate(run):
    ans = {"en": answers(run.input("titles_en")), "de": answers(run.input("titles_de"))}
    cur = {lang: {t: r.get("title") for t, r in a.items()} for lang, a in ans.items()}

    def rec(lang, title):
        return IRI(JL + f"dbpedia/{lang}/" + identifiers.title_iri_part(title))

    def res(lang, title):
        return IRI(RESOURCE[lang] + identifiers.title_iri_part(title))

    def art(lang, title):
        return IRI(ARTICLE[lang] + identifiers.title_iri_part(title))

    # 1. the selection
    rows = set()
    for name, ref in {**LINKED, "previous": INPUTS["previous"]}.items():
        slug = ref.split("/", 1)[0]
        for _s, p, o in run.triples(name):
            x = identifiers.identify(o, p)
            if x and x[0] in q.LANGS and q.is_article(x[1]) and (name == "previous" or identifiers.selects(slug, p, x[0])):
                rows.add((x[0], x[1], slug))
    t, stats = set(), {}
    current = {lang: {c for c in cur[lang].values() if c} for lang in cur}

    # 2. the records of the current articles
    items = {}
    for lang, a in ans.items():
        for r in a.values():
            if r.get("title") and r.get("item"):
                items[(lang, r["title"])] = r["item"]
    for lang, titles in current.items():
        for title in sorted(titles):
            r = rec(lang, title)
            t.add((r, IRI(SAME), IRI(canonical(str(res(lang, title))))))
            t.add((r, IRI(FOAF + "isPrimaryTopicOf"), art(lang, title)))
            t.add((r, IRI(SKOS + "prefLabel"), Literal(title.replace("_", " "), None, lang)))
            if (lang, title) in items:
                t.add((r, IRI(SAME), IRI(WD + items[(lang, title)])))
        stats[f"records {lang}"] = len(titles)

    # 3. the records of dbpedia-persons
    old_lang = {}
    for s, p, o in run.triples("previous"):
        if str(s).startswith(OLD) and p == SAME:
            x = identifiers.identify(o, p)
            name = identifiers.wiki_title(str(s)[len(OLD):])
            if x and x[0] in q.LANGS and x[1] == name:
                lang = q.LANGS[x[0]]
                if old_lang.get(str(s)) != "en":   # the English article where both have the name
                    old_lang[str(s)] = lang
    moved = {}
    for s, lang in old_lang.items():
        name = identifiers.wiki_title(s[len(OLD):])
        c = cur[lang].get(name)
        if c:
            moved[s] = rec(lang, c)
            t.add((IRI(s), IRI(REPLACED), moved[s]))
        else:
            t.add((IRI(s), IRI(DEPRECATED), Literal("true", XSD + "boolean")))
            run.log("dbpedia-persons record without a current article:", s)
    for s, p, o in run.triples("previous"):
        if str(s) in moved and not (p == SAME and identifiers.identify(o, p) and
                                    identifiers.identify(o, p)[0] in q.LANGS):
            t.add((moved[str(s)], p, o))
    stats["dbpedia-persons records moved"] = len(moved)
    stats["dbpedia-persons records without an article (deprecated)"] = len(old_lang) - len(moved)
    stats["dbpedia-persons records of no English or German article"] = len(
        {str(s) for s, _p, _o in run.triples("previous") if str(s).startswith(OLD)} - set(old_lang))

    # 4. redirects and missing titles
    for lang, a in ans.items():
        for asked, r in a.items():
            if r.get("title") and r["title"] != identifiers.wiki_title(asked):
                t.add((res(lang, asked), IRI(REPLACED), res(lang, r["title"])))
                t.add((art(lang, asked), IRI(REPLACED), art(lang, r["title"])))
                stats[f"titles replaced {lang}"] = stats.get(f"titles replaced {lang}", 0) + 1
            elif not r.get("title"):
                t.add((res(lang, asked), IRI(DEPRECATED), Literal("true", XSD + "boolean")))
                stats[f"titles missing {lang}"] = stats.get(f"titles missing {lang}", 0) + 1

    with gzip.open(run.path("dbpedia-selection.tsv.gz"), "wt", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["source", "title", "current", "reason", "detail"])
        for src, title, slug in sorted(rows):
            w.writerow([src, title, cur[q.LANGS[src]].get(title) or "", "linked", slug])
    run.note("; ".join(f"{k} {v:,}" for k, v in sorted(stats.items())) + f"; selection rows {len(rows):,}.")
    run.write_turtle("dbpedia.ttl.gz", set(canonical_triples(t)))   # docs/iri-forms.md
