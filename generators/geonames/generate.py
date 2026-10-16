"""geonames: the GeoNames features JudaicaLink uses (decision 0029), made from the GeoNames dump.

1. The selection list (geonames-selection.tsv.gz): one row per GeoNames id and dataset that links it (an IRI of
   GeoNames in any form, or our record data/geonames/<id>, as object; jl.identifiers), with the current id: the id
   itself if the feature is in the dump, empty if it is not (GeoNames publishes no cumulative list of merged or
   deleted features, so no successor can be stated).
2. The data (geonames.ttl.gz): every linked feature of the dump as a record data/geonames/<id>: owl:sameAs
   <https://sws.geonames.org/<id>/>, schema:Place, skos:prefLabel (the name), skos:altLabel (the alternate names, with
   their language where it is a language: not postal codes, airport and other codes, abbreviations, links),
   geosparql:asWKT, gn:featureClass and gn:featureCode, gn:countryCode, gn:population (if given), gn:parentADM1 (the
   first-level administrative division), foaf:isPrimaryTopicOf the Wikipedia articles and owl:sameAs the Wikidata
   item that GeoNames gives (alternate names of the kinds link and wkdt). External IRIs in canonical form (jl.iris);
   links to JudaicaLink are left out (0029).
"""

import csv
import gzip
import io
import re
import zipfile
from collections import defaultdict

from jl import identifiers
from jl import classes
from jl.generator import stable_inputs
from jl.iris import canonical
from jl.rdf import IRI, RDF_TYPE, XSD, Literal
from jl.turtle import PREFIXES

# the stable versions that may link GeoNames (all except ep, made from the others, and the ones without links to
# records); gnd and geo-enriched as their latest runs until they are versions
LINKED = stable_inputs("linked_", exclude={"geonames", "gnd-persons", "gnd-persons-entityfacts", "ep",
                                           "compact-memory", "compact-memory-supp", "cm-ocr-quality", "cm-tagme",
                                           "corrections-links", "quality-annotations", "judaicalink-agents",
                                           "judaicalink-vocabulary", "ontology"})
DUMP = "inputs:geonames/dump-2026-10-15/"
INPUTS = {"all": DUMP + "allCountries.zip", "alternate": DUMP + "alternateNamesV2.zip",
          "admin1": DUMP + "admin1CodesASCII.txt", **LINKED}
PARAMS = {}

JL = "http://data.judaicalink.org/data/"
SWS = "https://sws.geonames.org/"
GN = "http://www.geonames.org/ontology#"
JLO, SKOS, OWL, FOAF, GEO = (PREFIXES[p] for p in ("jl", "skos", "owl", "foaf", "geosparql"))
SAME = OWL + "sameAs"
LANGUAGE = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")   # not post, iata, icao, link, wkdt, fr_1793, ...
BAD_IRI = re.compile(r'[<>"{}|^`\\\s]')


def iri(x):
    return IRI(canonical(BAD_IRI.sub(lambda m: "%{:02X}".format(ord(m.group(0))), x.strip())))


def lines(path, member):
    with zipfile.ZipFile(path) as z, z.open(member) as f:
        yield from io.TextIOWrapper(f, encoding="utf-8")


def generate(run):
    linked = identifiers.scan(run, LINKED, {"geonames"}).get("geonames", {})
    wanted = set(linked)
    run.log(f"linked: {len(wanted):,} GeoNames ids")

    rows = {}
    for line in lines(run.input("all"), "allCountries.txt"):
        gid = line.split("\t", 1)[0]
        if gid in wanted:
            rows[gid] = line.rstrip("\n").split("\t")
    alt = defaultdict(set)
    for line in lines(run.input("alternate"), "alternateNamesV2.txt"):
        c = line.split("\t", 3)
        if len(c) > 2 and c[1] in rows:
            f = line.rstrip("\n").split("\t")
            alt[f[1]].add((f[2], f[3]))
    admin1 = {}
    with open(run.input("admin1"), encoding="utf-8") as f:
        for r in csv.reader(f, delimiter="\t"):
            if len(r) >= 4:
                admin1[r[0]] = r[3]

    t = set()
    counts = defaultdict(int)
    for gid, c in sorted(rows.items()):
        rec = IRI(JL + "geonames/" + gid)
        t |= {(rec, IRI(SAME), IRI(SWS + gid + "/")), (rec, IRI(RDF_TYPE), IRI(classes.PLACE)),
              (rec, IRI(SKOS + "prefLabel"), Literal(c[1]))}
        lat, lon = c[4], c[5]
        t.add((rec, IRI(GEO + "asWKT"), Literal(f"POINT({float(lon)} {float(lat)})", GEO + "wktLiteral")))
        if c[6]:
            t.add((rec, IRI(GN + "featureClass"), IRI(GN + c[6])))
            if c[7]:
                t.add((rec, IRI(GN + "featureCode"), IRI(f"{GN}{c[6]}.{c[7]}")))
        if c[8]:
            t.add((rec, IRI(GN + "countryCode"), Literal(c[8])))
            a1 = admin1.get(f"{c[8]}.{c[10]}") if c[10] else None
            if a1 and a1 != gid:
                t.add((rec, IRI(GN + "parentADM1"), IRI(SWS + a1 + "/")))
        if c[14] and c[14] != "0":
            t.add((rec, IRI(GN + "population"), Literal(c[14], XSD + "integer")))
        for lang, name in sorted(alt.get(gid, ())):
            if lang == "link":
                if re.match(r"^https?://[a-z-]+\.wikipedia\.org/wiki/", name) and not identifiers.is_ours(name):
                    t.add((rec, IRI(FOAF + "isPrimaryTopicOf"), iri(name)))
                    counts["wikipedia"] += 1
            elif lang == "wkdt":
                if re.fullmatch(r"Q[0-9]+", name):
                    t.add((rec, IRI(SAME), iri("http://www.wikidata.org/entity/" + name)))
                    counts["wikidata"] += 1
            elif not lang or LANGUAGE.match(lang):
                if name != c[1] or lang:
                    t.add((rec, IRI(SKOS + "altLabel"), Literal(name, None, lang or None)))
    missing = sorted(wanted - set(rows), key=int)
    for gid in missing:
        run.log("not in the dump:", gid, ", ".join(sorted(linked[gid])))

    with gzip.open(run.path("geonames-selection.tsv.gz"), "wt", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["geonames", "current", "reason", "detail"])
        for gid in sorted(wanted, key=int):
            for slug in sorted(linked[gid]):
                w.writerow([gid, gid if gid in rows else "", "linked", slug])
    by_ds = defaultdict(int)
    for gid, slugs in linked.items():
        for s in slugs:
            by_ds[s] += 1
    run.note(f"{len(rows):,} records of {len(wanted):,} linked ids ({len(missing):,} not in the dump); by dataset: "
             + ", ".join(f"{s} {n:,}" for s, n in sorted(by_ds.items(), key=lambda x: -x[1]))
             + f"; {counts['wikipedia']:,} Wikipedia articles, {counts['wikidata']:,} Wikidata items.")
    run.write_turtle("geonames.ttl.gz", t)
