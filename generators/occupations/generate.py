"""occupations: the occupations of JudaicaLink (kind vocabulary). All statements about occupations are here; the
datasets only link to them (gnd: jl:occupationURI, the GND subject headings it names as occupations).

1. The GND subject headings used as occupations, with their broader headings up to the top, from the GND dump:
   skos:Concept, skos:prefLabel and skos:altLabel (the GND's names, German), skos:broader (the GND's broader terms:
   general, generic, instantial, partitive) and gndo:gndSubjectCategory. The IRIs are the GND's: no IRIs of our own,
   so no entity pages.
2. The occupation IRIs of the older datasets, data/occupation/<name>: coined from names by gnd-persons (the GND's
   German names) and dbpedia-persons (English DBpedia categories) in 2018, carried on by records-normalized, bhr, sosy
   and dbpedia, and never described. Each gets skos:Concept, skos:prefLabel (the name, with its language) and
   skos:exactMatch the GND heading: NAMES below where it has the name (the English names, chosen by hand: matching
   them by name finds false friends, e.g. the GND's "Artist" is a circus or variety artiste); else the heading of
   exactly that name (German), or the one heading that has it as a variant name (older spellings: "Lexikograph"),
   preferring the headings used as occupations. A name without a heading gets no link.
"""

import gzip
import re
import unicodedata
import urllib.parse
from collections import Counter, defaultdict

from jl.generator import slug_of, stable_inputs
from jl.iris import canonical
from jl.rdf import IRI, RDF_TYPE, Literal, parse_ntriples
from jl.turtle import PREFIXES

# the datasets that state occupation IRIs (data/occupation/…) or GND occupations (gnd)
SOURCES = {"gnd", "records-normalized", "bhr", "sosy", "dbpedia"}
INPUTS = {
    "lds": "inputs:gnd/lds-2026-02-17/authorities-gnd_lds_20260217.nt.gz",
    **{k: v for k, v in stable_inputs().items() if slug_of(v) in SOURCES},
}
PARAMS = {}

# the English names of the older occupation IRIs (dbpedia-persons): their GND heading, chosen by hand (None: none)
NAMES = {
    "Rabbi": "4176751-2",   # Rabbiner: the GND's "Rabbi" (4485929-6) are the sages of the Talmudic period; bhr and
                            # DBpedia mean rabbis of all times
    "musician": "4040841-3", "writer": "4053309-8", "singer": "4124099-6", "sportspeople": "4056399-6",
    "artist": "4033423-5", "poet": "4168391-2", "composer": "4032009-1", "historian": "4025098-2",
    "Hebrew Bible people": "4006473-6", "chess player": "4179279-8", "architect": "4002844-6",
    "scientist": "4066567-7", "philosopher": "4045790-4", "inventor": "4015222-4", "politician": "4046517-2",
    "philanthropist": "1143159993", "physician": "4003157-3", "activist": "4434804-6", "Hazzan": "4323418-5",
    "scholar": "4156443-1", "fashion designer": "4233568-1", "educator": "4044300-0", "engineer": "4026955-3",
    "Judaic scholar": "7540491-6", "military personnel": "4055409-0", "art collector": "4166042-0",
    "Court Jew": "4160404-0", "psychiatrist": "4047666-2", "explorer": "4017917-5", "priest": "4047233-4",
    "religious leader": "4227685-8", "Prophets in Judaism": "4175942-4",
    "Mohel": None, "Rebbetzin": None,
}

JL = "http://data.judaicalink.org/data/"
OCC = JL + "occupation/"
GND = "https://d-nb.info/gnd/"
GNDO = PREFIXES["gndo"]
JLO, SKOS = PREFIXES["jl"], PREFIXES["skos"]
BROADER = {GNDO + "broaderTerm" + k for k in ("General", "Generic", "Instantial", "Partitive")}
WANTED = {GNDO + "preferredNameForTheSubjectHeading", GNDO + "variantNameForTheSubjectHeading",
          GNDO + "gndSubjectCategory"} | BROADER
LINE = re.compile(r"^<https://d-nb\.info/gnd/([0-9X-]+)> <(" + "|".join(re.escape(p) for p in WANTED) + ")> ")


def nfc(s):
    return unicodedata.normalize("NFC", s)


def headings(run):
    """The subject headings of the dump: {number: {"pref": name, "alt": [names], "broader": [numbers], "sc": [IRIs]}}."""
    out = defaultdict(lambda: {"pref": None, "alt": [], "broader": [], "sc": []})
    with gzip.open(run.input("lds"), "rt", encoding="utf-8") as f:
        for line in f:
            m = LINE.match(line)
            if not m:
                continue
            for _s, p, o in parse_ntriples([line]):
                h = out[m.group(1)]
                if p.endswith("preferredNameForTheSubjectHeading"):
                    h["pref"] = nfc(o.value)
                elif p.endswith("variantNameForTheSubjectHeading"):
                    h["alt"].append(nfc(o.value))
                elif p in BROADER and o.startswith(GND):
                    h["broader"].append(o[len(GND):])
                elif p.endswith("gndSubjectCategory"):
                    h["sc"].append(str(o))
    return {n: h for n, h in out.items() if h["pref"]}


def generate(run):
    used = Counter()   # GND headings named as occupations (gnd)
    for _s, p, o in run.triples("gnd"):
        if p == JLO + "occupationURI" and o.startswith(GND):
            used[o[len(GND):]] += 1
    older = Counter()   # occupation IRIs of the older datasets
    for name in INPUTS:
        if name in ("lds", "gnd"):
            continue
        for _s, _p, o in run.triples(name):
            if isinstance(o, str) and not isinstance(o, Literal) and o.startswith(OCC):
                older[o] += 1
    run.log(f"{len(used):,} GND headings used as occupations, {len(older):,} older occupation IRIs")

    heads = headings(run)
    run.log(f"{len(heads):,} subject headings in the dump")
    by_name, by_variant = defaultdict(list), defaultdict(list)
    for n, h in heads.items():
        by_name[h["pref"]].append(n)
        for alt in set(h["alt"]):
            by_variant[alt].append(n)

    t, matches, unmatched = set(), {}, []
    for iri in sorted(older):
        name = nfc(urllib.parse.unquote(iri[len(OCC):]).replace("_", " "))
        if name in NAMES:
            lang, n = "en", NAMES[name]
        else:
            found = by_name.get(name, []) or by_variant.get(name, [])
            preferred = [n for n in found if n in used] or found
            lang, n = ("de", preferred[0]) if len(preferred) == 1 else (None, None)
            if len(preferred) > 1:
                run.log(f"several headings named {name!r}: {', '.join(preferred)}")
        t.add((IRI(iri), IRI(RDF_TYPE), IRI(SKOS + "Concept")))
        t.add((IRI(iri), IRI(SKOS + "prefLabel"), Literal(name, lang=lang)))
        if n:
            if n not in heads:
                raise ValueError(f"NAMES: {name!r} names {n}, which is not a subject heading of the dump")
            t.add((IRI(iri), IRI(SKOS + "exactMatch"), IRI(GND + n)))
            matches[iri] = n
        else:
            unmatched.append((older[iri], name, lang))
    for k, name, lang in sorted(unmatched, reverse=True):
        run.log(f"no GND heading: {name!r} ({lang or 'language unknown'}, {k:,} statements)")

    # the headings: used, matched, and their broader headings up to the top
    todo, described = set(used) | set(matches.values()), set()
    missing = sorted(n for n in todo if n not in heads)
    while todo:
        n = todo.pop()
        if n in described or n not in heads:
            continue
        described.add(n)
        todo |= set(heads[n]["broader"])
    for n in sorted(described):
        h, iri = heads[n], IRI(GND + n)
        t.add((iri, IRI(RDF_TYPE), IRI(SKOS + "Concept")))
        t.add((iri, IRI(SKOS + "prefLabel"), Literal(h["pref"], lang="de")))
        for alt in h["alt"]:
            if alt != h["pref"]:
                t.add((iri, IRI(SKOS + "altLabel"), Literal(alt, lang="de")))
        for b in h["broader"]:
            if b in heads:
                t.add((iri, IRI(SKOS + "broader"), IRI(GND + b)))
        for sc in h["sc"]:
            t.add((iri, IRI(GNDO + "gndSubjectCategory"), IRI(canonical(sc))))
    for n in missing:
        run.log(f"used heading not in the dump: {n}")
    run.note(f"{len(used):,} GND headings used as occupations ({sum(used.values()):,} statements in gnd), "
             f"{len(described):,} described with their broader headings; {len(older):,} older occupation IRIs, "
             f"{len(matches):,} linked to a GND heading ({len(unmatched)} without)")
    run.write_turtle("occupations.ttl.gz", t)
