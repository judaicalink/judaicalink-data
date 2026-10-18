"""The quality of identity links: random samples with evidence, verdicts, accuracy per dataset and property.

sample(): for every unit (dataset, property, source) of candidate identity statements (identifiers.IDENTITY, and the
Wikipedia links foaf:isPrimaryTopicOf, foaf:page), a random sample of its links (fixed seed; all links of a small
unit), each with the evidence of both sides: the facts of the source record (names, dates, places, classes, the
beginning of its description) and of the target, our record of it in the authority dataset (gnd, lc, viaf, wikidata,
geonames; a Wikipedia article through the Wikidata item that has it). Writes <unit>.jsonl per unit into a directory.

The verdicts (correct, wrong, undecidable, with a reason) are written next to them as <unit>.verdicts.jsonl, one
line {"i": …, "verdict": …, "reason": …} per link. report() computes the accuracy correct / (correct + wrong) per unit
with its 95% interval (Wilson) and the share of undecidable links.
"""

import json
import math
import random
import re
from collections import defaultdict
from pathlib import Path

from . import authorities, catalog, corrections, generator, identifiers, rdf
from .turtle import PREFIXES

JL = "http://data.judaicalink.org/data/"
FOAF, SKOS, RDFS, JLO = PREFIXES["foaf"], PREFIXES["skos"], PREFIXES["rdfs"], PREFIXES["jl"]
CANDIDATES = identifiers.IDENTITY | {FOAF + "isPrimaryTopicOf", FOAF + "page"}
LABELS = {SKOS + "prefLabel", FOAF + "name", RDFS + "label", "http://purl.org/dc/terms/title",
          "http://purl.org/dc/elements/1.1/title", "https://d-nb.info/standards/elementset/gnd#preferredNameForThePerson",
          "http://www.loc.gov/mads/rdf/v1#authoritativeLabel"}
FACTS = {JLO + "birthDate": "birth", JLO + "deathDate": "death", JLO + "birthLocation": "birthplace",
         JLO + "deathLocation": "deathplace", JLO + "occupation": "occupation",
         "https://d-nb.info/standards/elementset/gnd#biographicalOrHistoricalInformation": "about",
         JLO + "hasAbstract": "about", JLO + "describedAt": "page", SKOS + "altLabel": "alt",
         "https://www.geonames.org/ontology#featureCode": "featureCode", "https://www.geonames.org/ontology#countryCode": "country",
         "http://www.wikidata.org/prop/direct/P31": "instanceOf"}
NS = {"gnd": "gnd/", "lc-names": "lc/", "viaf": "viaf/", "wikidata": "wikidata/", "geonames": "geonames/"}
AUTH_SLUG = {"gnd": "gnd", "lc-names": "lc", "viaf": "viaf", "wikidata": "wikidata", "geonames": "geonames"}
MAX = {"label": 4, "alt": 4, "about": 1, "occupation": 3, "page": 2, "instanceOf": 3}


def unit_name(slug, prop, source):
    local = re.split(r"[#/]", prop.rstrip("/"))[-1]
    return f"{slug}--{local}--{source}"


def facts_of(triples, wanted):
    out = defaultdict(lambda: defaultdict(list))
    for s, p, o in triples:
        s = str(s)
        if s not in wanted:
            continue
        key = "label" if p in LABELS else FACTS.get(str(p))
        if p == rdf.RDF_TYPE and not isinstance(o, rdf.Literal):
            key, val = "class", str(o).rsplit("/", 1)[-1].rsplit("#", 1)[-1]
        elif key:
            val = o.value if isinstance(o, rdf.Literal) else str(o)
            if key == "about":
                val = val[:400]
        else:
            continue
        if len(out[s][key]) < MAX.get(key, 3) and val not in out[s][key]:
            out[s][key].append(val)
    return {s: dict(v) for s, v in out.items()}


def resolve_refs(cfg, cat, use, skip):
    generator.USE.clear()
    generator.USE.update(use)
    try:
        refs = generator.stable_inputs(exclude=skip)
    finally:
        generator.USE.clear()
    return refs


def sample(cfg, out, use=None, size=100, small=150, seed=2026, only=None, log=print):
    use = use or {}
    cat = catalog.Catalog()
    deleted = set()
    for c_slug, c_version, c_path, _local in corrections.stable_deletions(cat):
        f = generator.resolve(cfg, cat, f"{c_slug}/{c_version}/{c_path}")[0]
        deleted.update(corrections.key(t) for t in corrections.read(f["path"]))
    refs = resolve_refs(cfg, cat, use, authorities.NOT_LINKING)

    def triples(ref):
        for f in generator.resolve(cfg, cat, ref):
            for t in rdf.read_triples(f["path"]):
                if not deleted or corrections.key(t) not in deleted:
                    yield t

    # 1. the links per unit
    units = defaultdict(list)
    for ref in sorted(refs.values()):
        slug = generator.slug_of(ref)
        if only and slug not in only:
            continue
        own = authorities.SOURCE.get(slug)
        for s, p, o in triples(ref):
            if str(p) not in CANDIDATES or not str(s).startswith(JL):
                continue
            x = identifiers.identify(o, p)
            if not x or x[0] == own or (x[0] not in NS and not x[0].startswith("wikipedia-")):
                continue
            units[(slug, str(p), x[0])].append((str(s), x[1], str(o)))
        log(f"  links of {ref}: {sum(len(v) for k, v in units.items() if k[0] == slug):,}")

    # 2. the samples
    chosen = {}
    for key, links in units.items():
        links = sorted(set(links))
        rnd = random.Random(f"{seed}:{unit_name(*key)}")
        chosen[key] = links if len(links) <= small else rnd.sample(links, size)

    # 3. evidence: the source records, the authority records, Wikipedia through Wikidata
    by_slug = defaultdict(set)
    for (slug, _p, _src), links in chosen.items():
        by_slug[slug] |= {s for s, _i, _o in links}
    src_facts = {}
    for ref in refs.values():
        slug = generator.slug_of(ref)
        if by_slug.get(slug):
            src_facts.update(facts_of(triples(ref), by_slug[slug]))
    auth = {}
    for source, slug in AUTH_SLUG.items():
        ref = authorities.selection_ref(cat, slug, use)
        if ref is None:
            continue
        a = authorities.Authority(source, slug)
        a.read(triples(f"{slug}/{ref}"))
        auth[source] = (a, f"{slug}/{ref}")
    want = defaultdict(set)
    wiki_titles = defaultdict(set)
    for (_slug, _p, src), links in chosen.items():
        for _s, ident, _o in links:
            if src in auth:
                cur, _st = auth[src][0].current(ident)
                want[src] |= {JL + NS[src] + c for c in cur}
            elif src.startswith("wikipedia-"):
                wiki_titles[src].add(ident)
    wiki_item = {}
    if "wikidata" in auth:
        for s, p, o in triples(auth["wikidata"][1]):
            if str(p) == FOAF + "isPrimaryTopicOf":
                x = identifiers.identify(o, p)
                if x and x[1] in wiki_titles.get(x[0], ()):
                    wiki_item[(x[0], x[1])] = str(s)
        want["wikidata"] |= set(wiki_item.values())
    tgt_facts = {}
    for src, (a, ref) in auth.items():
        tgt_facts.update(facts_of(triples(ref), want[src]))

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    summary = []
    for key, links in sorted(chosen.items()):
        slug, p, src = key
        name = unit_name(*key)
        with open(out / f"{name}.jsonl", "w", encoding="utf-8") as f:
            for i, (s, ident, o) in enumerate(links):
                target = {"identifier": ident, "iri": o}
                if src in auth:
                    cur, status = auth[src][0].current(ident)
                    target["status"] = status
                    target["records"] = [{"iri": JL + NS[src] + c, **tgt_facts.get(JL + NS[src] + c, {})} for c in sorted(cur)]
                elif (src, ident) in wiki_item:
                    w = wiki_item[(src, ident)]
                    target["status"] = "through the Wikidata item that has this article"
                    target["records"] = [{"iri": w, **tgt_facts.get(w, {})}]
                else:
                    target["status"] = "no record of the target in our data"
                    target["records"] = []
                f.write(json.dumps({"i": i, "unit": name, "source": {"iri": s, **src_facts.get(s, {})},
                                    "target": target}, ensure_ascii=False) + "\n")
        summary.append({"unit": name, "dataset": slug, "property": p, "source": src,
                        "links": len(units[key]), "sample": len(links)})
    (out / "units.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def report(directory):
    """[(unit info, counts, accuracy, interval)] from the verdict files."""
    d = Path(directory)
    rows = []
    for u in json.loads((d / "units.json").read_text(encoding="utf-8")):
        vf = d / f"{u['unit']}.verdicts.jsonl"
        counts = defaultdict(int)
        if vf.is_file():
            for line in vf.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    counts[json.loads(line)["verdict"]] += 1
        n = counts["correct"] + counts["wrong"]
        rows.append((u, dict(counts), counts["correct"] / n if n else None, wilson(counts["correct"], n)))
    return rows
