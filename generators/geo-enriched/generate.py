"""geo-enriched: the birth and death places of six record datasets as IRIs (jl:birthLocationURI, jl:deathLocationURI).

Made again from the source records (decision 0024), offline and deterministically; the version of 2019 took the first
hit of the GeoNames search for every place name, without disambiguation (Jerusalem as West Jerusalem, Bonn as its
airport, Karlsbad as Carlsbad in California, Lissa as the island of Vis), and its generator is lost.

For every jl:birthLocation / jl:deathLocation text of the stable versions of bhr, djh, gnd-persons, haskala,
hirsch-family and ubffm-persons:
1. if the text is the label of exactly one place of geo-coordinates (compared like records-normalized: whitespace
   collapsed, case ignored), that place (data/geo-coordinates/<name>, which has its GND and GeoNames links);
2. otherwise the GeoNames record chosen by gazetteer.py from the GeoNames dump (name, qualifier, population; ambiguous
   names are left out): the geo-coordinates place with that GeoNames id if there is exactly one, else our record of
   the GeoNames feature, data/geonames/<id> (dataset geonames, decision 0029; the 2019 version linked the same IRIs).
   Nothing is copied from GeoNames (its data is CC BY 4.0).
"""

import re
from collections import Counter, defaultdict

from jl.rdf import IRI, Literal
from jl.turtle import PREFIXES

import gazetteer

SOURCES = {"bhr": "bhr/2026-10-12", "djh": "djh/2018-10-22", "gnd_persons": "gnd-persons/2018-11-29",
           "haskala": "haskala/2026-10-12", "hirsch_family": "hirsch-family/2018-10-30",
           "ubffm_persons": "ubffm-persons/2019-01-24"}
INPUTS = {**SOURCES, "geo_coordinates": "geo-coordinates/2026-10-12",
          "previous": "geo-enriched/2019-12-18",
          "geonames": "inputs:geonames/dump-2026-10-15/allCountries.zip",
          "geonames_alt": "inputs:geonames/dump-2026-10-15/alternateNamesV2.zip"}
PARAMS = {}

JLO = PREFIXES["jl"]
JL = "http://data.judaicalink.org/data/"
SAME = PREFIXES["owl"] + "sameAs"
GEONAMES_ID = re.compile(r"^https?://(?:sws\.|www\.)?geonames\.org/([0-9]+)/?$")
PROPS = {JLO + "birthLocation": JLO + "birthLocationURI", JLO + "deathLocation": JLO + "deathLocationURI"}


def label_key(s):   # as records-normalized compares place names
    return re.sub(r"\s+", " ", s).strip().lower()


def geonames_iri(gid):
    return f"{JL}geonames/{gid}"   # our record of the feature (dataset geonames)


def generate(run):
    # the place texts of the records
    statements = []
    for name in SOURCES:
        for s, p, o in run.triples(name):
            if p in PROPS and isinstance(o, Literal):
                statements.append((name, str(s), PROPS[p], o.value))
    texts = sorted({lit for _, _, _, lit in statements})
    run.log(f"{len(statements):,} place statements, {len(texts):,} distinct texts")

    # geo-coordinates: labels and GeoNames ids
    by_label, gc_geonames = defaultdict(set), defaultdict(set)
    for s, p, o in run.triples("geo_coordinates"):
        if p == PREFIXES["skos"] + "prefLabel" and isinstance(o, Literal):
            by_label[label_key(o.value)].add(str(s))
        elif p == SAME:
            m = GEONAMES_ID.match(str(o))
            if m:
                gc_geonames[m.group(1)].add(str(s))

    # every text once: its place IRI or the reason why none
    target, how = {}, {}
    rest = {}
    for lit in texts:
        places = by_label.get(label_key(lit), set())
        if len(places) == 1:
            target[lit], how[lit] = next(iter(places)), "geo-coordinates label"
            continue
        name, qualifier = gazetteer.clean(lit)
        if name is None:
            how[lit] = qualifier   # the reason
            continue
        rest[lit] = (name, qualifier)
    run.log(f"{len(target):,} texts are geo-coordinates labels; looking up {len(rest):,} in the GeoNames dump")
    names = {n for n, _ in rest.values()} | {gazetteer.normal(lit) for lit in rest}
    gaz = gazetteer.Gazetteer(run.input("geonames"), run.input("geonames_alt"), names,
                              {q for _, q in rest.values() if q})
    for lit in sorted(rest):
        rec, why = gaz.choose_text(lit)
        if rec is None:
            how[lit] = why
            continue
        gc = gc_geonames.get(rec["id"], set())
        if len(gc) == 1:
            target[lit], how[lit] = next(iter(gc)), f"GeoNames ({why}), a geo-coordinates place"
        else:
            target[lit], how[lit] = geonames_iri(rec["id"]), f"GeoNames ({why})"
        run.log(f"  {lit!r} -> {rec['id']} {rec['name']} ({rec['code']}, {rec['cc']}, pop. {rec['pop']:,}): {how[lit]}")
    for lit in sorted(set(texts) - set(target)):
        run.log(f"  {lit!r}: not linked, {how[lit]}")

    t = set()
    stats = Counter()
    for name, s, prop, lit in statements:
        if lit in target:
            t.add((IRI(s), IRI(prop), IRI(target[lit])))
            stats[(name, "linked")] += 1
        else:
            stats[(name, "not linked")] += 1

    reasons = Counter(how[lit].split(" (")[0] if lit not in target else how[lit] for lit in texts)
    run.note(f"{len(statements):,} place statements of {len(texts):,} distinct texts; texts: "
             + ", ".join(f"{k} {v:,}" for k, v in sorted(reasons.items())) + "; statements: "
             + ", ".join(f"{n} {stats[(n, 'linked')]:,} of {stats[(n, 'linked')] + stats[(n, 'not linked')]:,}"
                         for n in SOURCES) + ".")
    run.write_turtle("geo-enriched.ttl.gz", t)
