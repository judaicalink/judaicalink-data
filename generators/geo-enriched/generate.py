"""geo-enriched: the birth and death places of six record datasets as IRIs (jl:birthLocationURI, jl:deathLocationURI).

Made again from the source records (decision 0024), offline and deterministically; the version of 2019 took the first
hit of the GeoNames search for every place name, without disambiguation (Jerusalem as West Jerusalem, Bonn as its
airport, Karlsbad as Carlsbad in California, Lissa as the island of Vis), and its generator is lost.

For every jl:birthLocation / jl:deathLocation text of the stable record and authority datasets that a record gives
without a place IRI (texts compared in NFC, whitespace collapsed, case ignored):
1. evidence (decided 2026-11-10): the places that our sources state together with the same text (a record with the
   text and a place IRI for it; GND, LC, …; not Wikidata, which the result is checked against), as GeoNames ids (the
   owl:sameAs of the place records). With two or more such records, the place of at least two thirds of them;
   if no place has two thirds, the text is ambiguous in our data and left out. One record makes its place the
   preferred candidate of step 3;
2. if the text is the label of exactly one place of geo-coordinates, that place (data/geo-coordinates/<name>, which
   has its GND and GeoNames links);
3. otherwise the GeoNames record chosen by gazetteer.py from the GeoNames dump: among the candidates of the name
   (and qualifier) the one stated for the text, else the place our sources name most often (place statements,
   place records, geo-coordinates places), else population; ambiguous names are left out.
A chosen GeoNames feature is linked as the geo-coordinates place with that GeoNames id if there is exactly one, else
as our record of the feature, data/geonames/<id> (dataset geonames, decision 0029). Nothing is copied from GeoNames
(its data is CC BY 4.0).
"""

import re
import unicodedata
from collections import Counter, defaultdict

from jl.generator import stable_inputs
from jl.rdf import IRI, Literal
from jl.turtle import PREFIXES

import gazetteer
from jl import classes
from jl.rdf import RDF_TYPE

# every record and authority dataset (decided 2026-10-16: only places given as text without an IRI are linked); gnd
# replaces gnd-persons.
SOURCES = stable_inputs(kinds={"records", "authority"})
INPUTS = {**SOURCES, "geo_coordinates": "geo-coordinates/2026-10-12",
          "previous": "geo-enriched/2019-12-18",
          "geonames_dump": "inputs:geonames/dump-2026-10-15/allCountries.zip",
          "geonames_dump_alt": "inputs:geonames/dump-2026-10-15/alternateNamesV2.zip"}
PARAMS = {}

JLO = PREFIXES["jl"]
JL = "http://data.judaicalink.org/data/"
SAME = PREFIXES["owl"] + "sameAs"
GEONAMES_ID = re.compile(r"^https?://(?:sws\.|www\.)?geonames\.org/([0-9]+)/?$")
PROPS = {JLO + "birthLocation": JLO + "birthLocationURI", JLO + "deathLocation": JLO + "deathLocationURI"}


def label_key(s):   # as records-normalized compares place names (NFC since 2026-11-10)
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s)).strip().lower()


EVIDENCE_SHARE = 2 / 3
NOT_EVIDENCE = {"wikidata"}   # the benchmark of the place links


def geonames_iri(gid):
    return f"{JL}geonames/{gid}"   # our record of the feature (dataset geonames)


def generate(run):
    # the place texts of the records
    statements, has_iri, skipped = [], set(), Counter()
    stated_texts, stated_iris = defaultdict(set), defaultdict(set)   # (record, property) -> texts / place IRIs
    places, same = set(), defaultdict(set)                            # place records and their owl:sameAs
    for name in SOURCES:
        found = []
        for s, p, o in run.triples(name):
            if p in PROPS and isinstance(o, Literal):
                found.append((name, str(s), PROPS[p], o.value))
                if name not in NOT_EVIDENCE:
                    stated_texts[(str(s), PROPS[p])].add(o.value)
            elif p in PROPS.values() and not isinstance(o, Literal):
                has_iri.add((str(s), p))
                if name not in NOT_EVIDENCE:
                    stated_iris[(str(s), p)].add(str(o))
            elif p == RDF_TYPE and classes.kind(o) == "Place":
                places.add(str(s))
            elif p == SAME and str(s) in places:
                same[str(s)].add(str(o))
        for st in found:   # only places given as text: a record with a place IRI for it is not enriched
            if (st[1], st[2]) in has_iri:
                skipped[name] += 1
            else:
                statements.append(st)
    run.log("place texts left out because the record has a place IRI: "
            + ", ".join(f"{k} {v:,}" for k, v in sorted(skipped.items())))
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

    # evidence: the GeoNames ids of the places our sources state for a text
    geonames_of = {}   # place IRI (the record and its owl:sameAs) -> GeoNames ids
    for s, objs in same.items():
        ids = frozenset(m.group(1) for o in objs for m in [GEONAMES_ID.match(o)] if m)
        if ids:
            for i in objs | {s}:
                geonames_of[i] = ids
    for gid, gcs in gc_geonames.items():
        for gc in gcs:
            geonames_of.setdefault(gc, frozenset({gid}))

    def ids_of(iri):
        m = GEONAMES_ID.match(iri) or re.match(re.escape(JL) + r"geonames/([0-9]+)$", iri)
        return frozenset({m.group(1)}) if m else geonames_of.get(iri)

    # how often our sources name a place: each place statement, each place record, each geo-coordinates place
    votes, freq = defaultdict(Counter), Counter()
    for k, iris in stated_iris.items():
        ids = {i for i in map(ids_of, iris) if i}
        for i in ids:
            freq.update(i)
        if len(ids) == 1:
            for lit in stated_texts.get(k, ()):
                votes[label_key(lit)][next(iter(ids))] += 1
    for s in same:
        freq.update(geonames_of.get(s, ()))
    freq.update(list(gc_geonames))
    run.log(f"evidence: {len(votes):,} texts stated with a place by our sources; {len(freq):,} GeoNames ids named")

    # every text once: its place IRI or the reason why none
    target, how = {}, {}
    rest, by_evidence, prefer = {}, {}, {}
    for lit in texts:
        v = votes.get(label_key(lit))
        if v:
            total = sum(v.values())
            ids, n = v.most_common(1)[0]
            if total >= 2 and n >= EVIDENCE_SHARE * total:
                by_evidence[lit] = (ids, f"stated by our sources for this text ({n} of {total})")
                continue
            if total >= 2:
                how[lit] = f"ambiguous in our data ({len(v)} places for {total} records)"
                continue
            prefer[lit] = ids
        places_gc = by_label.get(label_key(lit), set())
        if len(places_gc) == 1:
            target[lit], how[lit] = next(iter(places_gc)), "geo-coordinates label"
            continue
        name, qualifier = gazetteer.clean(lit)
        if name is None:
            how[lit] = qualifier   # the reason
            continue
        rest[lit] = (name, qualifier)
    run.log(f"{len(by_evidence):,} texts by evidence, {len(target):,} are geo-coordinates labels; looking up "
            f"{len(rest):,} in the GeoNames dump")
    names = {n for n, _ in rest.values()} | {gazetteer.normal(lit) for lit in rest}
    gaz = gazetteer.Gazetteer(run.input("geonames_dump"), run.input("geonames_dump_alt"), names,
                              {q for _, q in rest.values() if q}, {x for ids, _ in by_evidence.values() for x in ids})

    def link(lit, rec, why):
        gc = gc_geonames.get(rec["id"], set())
        if len(gc) == 1:
            target[lit], how[lit] = next(iter(gc)), f"{why}, a geo-coordinates place"
        else:
            target[lit], how[lit] = geonames_iri(rec["id"]), why
        run.log(f"  {lit!r} -> {rec['id']} {rec['name']} ({rec['code']}, {rec['cc']}, pop. {rec['pop']:,}): {how[lit]}")

    for lit, (ids, why) in sorted(by_evidence.items()):
        recs = [gaz.by_id[i] for i in sorted(ids) if i in gaz.by_id]
        if not recs:
            how[lit] = "stated place not in the GeoNames dump"
            continue
        # one place in several forms (city, municipality): a geo-coordinates place, else the populated place
        rec = min(recs, key=lambda r: (len(gc_geonames.get(r["id"], ())) != 1, r["class"] != "P",
                                       -gazetteer.pop(r), int(r["id"])))
        link(lit, rec, why)
    for lit in sorted(rest):
        rec, why = gaz.choose_text(lit, prefer.get(lit, ()), freq)
        if rec is None:
            how[lit] = why
            continue
        link(lit, rec, f"GeoNames ({why})")
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

    reasons = Counter(re.sub(r"\d[\d,]*", "n", how[lit].split(" (")[0] if lit not in target else how[lit])
                      for lit in texts)
    run.note(f"{len(statements):,} place statements of {len(texts):,} distinct texts; texts: "
             + ", ".join(f"{k} {v:,}" for k, v in sorted(reasons.items())) + "; statements: "
             + ", ".join(f"{n} {stats[(n, 'linked')]:,} of {stats[(n, 'linked')] + stats[(n, 'not linked')]:,}"
                         for n in SOURCES) + ".")
    run.write_turtle("geo-enriched.ttl.gz", t)
