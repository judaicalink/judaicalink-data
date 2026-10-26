"""The evidence for judging the VIAF numbers of the Footprints persons (input of the judging, not of the generator).

python3 evidence.py <store> <out.jsonl>

For every Footprints person with a VIAF number (owl:sameAs in footprints): its names (label, the aliases of its
actor records), its class (record-classes) and what it did (up to ROLES records that name it: the role, the work,
imprint, copy or footprint, its title, date and place; of a work the date and place of its earliest imprint, of a
footprint without a date the date of the imprint of its copy); and of the VIAF cluster (dataset viaf) the class, names
and life dates, with the GND record the cluster links (biographical note, places of birth and death) and the labels
of its Wikidata item. One JSON object per link, in the order of the person IRIs.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from jl import classes  # noqa: E402
from jl.rdf import RDF_TYPE, Literal, read_triples  # noqa: E402
from jl.turtle import PREFIXES  # noqa: E402

VERSIONS = {"footprints": "2026-10-26", "record-classes": "2026-10-26", "viaf": "2026-10-26", "gnd": "2026-10-26",
            "wikidata": "2026-10-26"}
JL = "http://data.judaicalink.org/data/"
FP, FPV = JL + "footprints/", JL + "footprints/vocab/"
VIAF_IRI = re.compile(r"https?://(?:www\.)?viaf\.org/viaf/([0-9]+)/?$")
SAME, LABEL, PREF, ALT = (PREFIXES["owl"] + "sameAs", PREFIXES["rdfs"] + "label", PREFIXES["skos"] + "prefLabel",
                          PREFIXES["skos"] + "altLabel")
JLO, GNDO = PREFIXES["jl"], PREFIXES["gndo"]
ROLES = 15
ALTS = 20
STRUCTURE = {FPV + "person", FPV + "actor", PREFIXES["dcterms"] + "isReplacedBy"}
DATES = (FPV + "publicationDate", FPV + "associatedDate")


def path(store, slug):
    return Path(store) / slug / VERSIONS[slug] / f"{slug}.ttl.gz"


def local(iri):
    return re.split(r"[/#]", iri)[-1]


def footprints(store):
    t = defaultdict(lambda: defaultdict(list))   # subject -> predicate -> objects
    refs = defaultdict(list)                       # person -> [(predicate, subject)]
    for s, p, o in read_triples(path(store, "footprints")):
        s = str(s)
        t[s][p].append(o)
        if not isinstance(o, Literal) and str(o).startswith(FP + "person/") and s.startswith(FP) and p not in STRUCTURE:
            refs[str(o)].append((p, s))
    aliases = defaultdict(set)                     # person -> the aliases of its actor records
    for a, ps in t.items():
        for o in ps.get(FPV + "person", ()):
            aliases[str(o)] |= {x.value for x in ps.get(FPV + "alias", ())}
    imprints = defaultdict(list)                   # work -> [(date, place)] of its imprints
    for i, ps in t.items():
        if i.startswith(FP + "imprint/"):
            for w in ps.get(FPV + "work", ()):
                imprints[str(w)].append((first(t, i, *DATES), first(t, i, FPV + "place")))
    return t, refs, aliases, imprints


def first(t, s, *ps):
    for p in ps:
        for o in t.get(s, {}).get(p, ()):
            return o.value if isinstance(o, Literal) else str(o)
    return None


def source_side(t, refs, aliases, imprints, cls, s):
    roles = []
    for p, r in refs.get(s, ()):
        date = first(t, r, *DATES)
        if date is None and FPV + "copy" in t.get(r, {}):   # a footprint: the date of the imprint of its copy
            imp = first(t, first(t, r, FPV + "copy"), FPV + "imprint")
            date = first(t, imp, *DATES) if imp else None
            date = f"printed {date}" if date else None
        place = first(t, r, FPV + "place")
        if r.startswith(FP + "writtenwork/") and imprints.get(r):   # a work: its earliest imprint
            date, place = min(imprints[r], key=lambda x: (x[0] or "~", x[1] or ""))
            date = f"printed {date}" if date else None
        roles.append({"as": local(p), "record": r[len(FP):], "title": first(t, r, FPV + "title", LABEL),
                      "date": date, "place": first(t, place, LABEL, PREF) if place else None})
    roles.sort(key=lambda x: (x["date"] or "~", x["record"]))
    return {"iri": s, "label": first(t, s, PREF, LABEL), "aliases": sorted(aliases.get(s, ())), "class": sorted(cls.get(s, ())),
            "roles": roles[:ROLES], "roles_total": len(roles)}


def records(store, slug, wanted):
    out = defaultdict(lambda: defaultdict(list))
    for s, p, o in read_triples(path(store, slug)):
        if str(s) in wanted:
            out[str(s)][p].append(o)
    return out


def values(ps, p, n=None):
    v = sorted({o.value if isinstance(o, Literal) else str(o) for o in ps.get(p, ())})
    return v[:n] if n else v


def main(store, out):
    t, refs, aliases, imprints = footprints(store)
    cls = defaultdict(set)
    for s, p, o in read_triples(path(store, "record-classes")):
        if p == RDF_TYPE and str(s).startswith(FP):
            cls[str(s)].add(classes.kind(str(o)))
    links = sorted((s, m.group(1)) for s, ps in t.items() if s.startswith(FP + "person/")
                   for o in ps.get(SAME, ()) if (m := VIAF_IRI.match(str(o))))
    viaf = records(store, "viaf", {JL + "viaf/" + n for _s, n in links})
    gnd_of, wd_of = {}, {}
    for v, ps in viaf.items():
        for o in map(str, ps.get(SAME, ())):
            if m := re.match(r"https://d-nb\.info/gnd/(.+)$", o):
                gnd_of.setdefault(v, JL + "gnd/" + m.group(1))
            elif m := re.match(r"http://www\.wikidata\.org/entity/(Q[0-9]+)$", o):
                wd_of.setdefault(v, JL + "wikidata/" + m.group(1))
    gnd = records(store, "gnd", set(gnd_of.values()))
    wd = records(store, "wikidata", set(wd_of.values()))
    with open(out, "w", encoding="utf-8") as f:
        for i, (s, n) in enumerate(links):
            v = JL + "viaf/" + n
            ps = viaf.get(v)
            target = {"viaf": n, "in_dataset": ps is not None}
            if ps:
                target |= {"class": sorted({classes.kind(str(o)) for o in ps.get(RDF_TYPE, ())} - {None}),
                           "label": values(ps, PREF), "alt": values(ps, ALT, ALTS),
                           "birth": values(ps, JLO + "birthDate"), "death": values(ps, JLO + "deathDate")}
                if (g := gnd.get(gnd_of.get(v))):
                    target["gnd"] = {"label": values(g, PREF), "info": values(g, GNDO + "biographicalOrHistoricalInformation"),
                                     "birthplace": values(g, JLO + "birthLocation"),
                                     "deathplace": values(g, JLO + "deathLocation"),
                                     "birth": values(g, JLO + "birthDate"), "death": values(g, JLO + "deathDate")}
                if (w := wd.get(wd_of.get(v))):
                    target["wikidata"] = {"label": values(w, PREF), "birth": values(w, JLO + "birthDate"),
                                          "death": values(w, JLO + "deathDate")}
            f.write(json.dumps({"i": i, "source": source_side(t, refs, aliases, imprints, cls, s), "target": target},
                               ensure_ascii=False) + "\n")
    print(f"{len(links):,} links, {sum(1 for _s, n in links if JL + 'viaf/' + n in viaf):,} with the cluster in viaf")


if __name__ == "__main__":
    main(*sys.argv[1:])
