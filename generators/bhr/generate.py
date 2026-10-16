"""bhr: a new version made from the version 2018-10-24 with the errors of its generator fixed (decision 0024).

The chain that made 2018-10-24 cannot be run again (crawl of 2017/18, a local GND in Fuseki, Python 2; README), so this
generator transforms the previous version. Each fix is a parameter with the fix as default; with all of them off, the
output has the same triples as 2018-10-24.

- drop_service_page: owl:sameAs <http://www.dnb.de/…/entityfacts_node.html>, the EntityFacts service page, which the
  generator stated for every person with a GND number (783); it identifies nothing.
- drop_empty: the links built for persons without a GND number, with an empty identifier (d-nb.info/gnd//,
  hub.culturegraph.org/entityfacts//, the Steinheim GND query with text1=/; 9), the empty literals (2,141: birth
  and death dates, publications, abstracts, GND numbers) and the placeholder "NA" for a missing GND number (1,692).
- split_mixed: the records of Glückmann and Gunzenhausen, which the integration grouped with Gutheim by their empty
  GND number, hold the BHR entries, abstracts and publications of all three; each keeps its own (MIXED: the death date
  stated in the record matches one abstract each; the BHR page order 372 < 398 < 399 is the alphabetical order of the
  three names; Gutheim's record holds only his own).
- occupation_uri: jl:occpation (a typo; 2,900, every person) with occupation IRIs as values becomes
  jl:occupationURI, the property for occupation IRIs (0020).
- portal_links: owl:sameAs <http://steinheim-institut.de:50580/cgi-bin/bhr?id=N>, the page of the person in the BHR
  database of 2018, which no longer answers (and a page is not the person), becomes jl:describedAt the page of the same
  id in the Biographisches Portal der Rabbiner, <https://www.steinheim-institut.de/cgi-bin/bhr?id=N> (the portal's own
  links and Wikidata P10405 use the id without leading zeros).
- portal_gnd: the GND numbers of the portal's BEACON (input inputs:bhr/portal-2026-10-15: the BEACON of 2025-06-05 and,
  for each number, the BHR id of the page it leads to) as owl:sameAs <http://d-nb.info/gnd/…> for the records of
  that id that have no GND link; a record with another GND number than the portal's keeps its own (named in the log),
  and so do ids held by two records.
"""

import csv

from jl.rdf import IRI, Literal
from jl.turtle import PREFIXES

INPUTS = {"previous": "bhr/2018-10-24", "portal": "inputs:bhr/portal-2026-10-15/gnd-bhr.tsv"}
PARAMS = {"drop_service_page": True, "drop_empty": True, "split_mixed": True, "occupation_uri": True,
          "portal_links": True, "portal_gnd": True}

JLO = PREFIXES["jl"]
OWL_SAME = PREFIXES["owl"] + "sameAs"
GNDID = "http://d-nb.info/standards/elementset/gnd#gndIdentifier"
BHR = "http://data.judaicalink.org/data/bhr/"
SERVICE_PAGE = "http://www.dnb.de/DE/Service/DigitaleDienste/EntityFacts/entityfacts_node.html"
EMPTY_IDS = {"http://d-nb.info/gnd//", "http://hub.culturegraph.org/entityfacts//",
             "http://www.steinheim-institut.de/see-also/query.html?kategorie1=GND&text1=/"}
STEINHEIM = "http://steinheim-institut.de:50580/cgi-bin/bhr?id="
PORTAL = "https://www.steinheim-institut.de/cgi-bin/bhr?id="
GND = "http://d-nb.info/gnd/"
# the record, its BHR id and the beginnings of its own abstract and publications
MIXED = {
    BHR + "Glückmann_David": ("572", ["Gest.  2. Juli 1851 in Pleszew"], []),
    BHR + "Gunzenhausen_IsakHirsch": ("638", ["Geb.  in Fürth,Gest.  Sept. 1881 in Binswangen"],
                                      ["Anfrage in Hamburger"]),
}
FILES = ("bhr-final-05.ttl.gz", "Entityfacts-bhr-sameas.ttl.gz")


def keep_mixed(s, p, o):
    """For a mixed record: is this one of its own values?"""
    bhr_id, abstracts, publications = MIXED[s]
    if p == OWL_SAME and o.startswith(STEINHEIM):
        return o == STEINHEIM + bhr_id
    if p == JLO + "describedAt":
        return o.value.endswith(f"id:{bhr_id}")
    if p == JLO + "hasAbstract":
        return any(o.value.startswith(a) for a in abstracts)
    if p == JLO + "hasPublication":
        return any(o.value.startswith(a) for a in publications)
    return True


def portal_gnd(run, files):
    """The links to add: (record, GND IRI) for the portal's GND numbers, from the cleaned triples of all files."""
    ids, gnds = {}, {}
    for triples in files.values():
        for s, p, o in triples:
            for prefix in (STEINHEIM, PORTAL):
                if p in (OWL_SAME, JLO + "describedAt") and isinstance(o, IRI) and o.startswith(prefix):
                    ids.setdefault(o[len(prefix):], set()).add(s)
            if p == OWL_SAME and isinstance(o, IRI) and o.startswith(GND):
                gnds.setdefault(s, set()).add(o[len(GND):].removesuffix("/about"))
    with open(run.input("portal"), encoding="utf-8", newline="") as f:
        portal = [(r["gnd"], r["bhr"].lstrip("0")) for r in csv.DictReader(f, delimiter="\t")]
    add, stats = set(), {}

    def count(k):
        stats[k] = stats.get(k, 0) + 1

    for gnd, bhr_id in sorted(portal):
        records = ids.get(bhr_id, set())
        if not bhr_id or not records:
            count("portal GND of an id we do not have")
            run.log("no record:", f"GND {gnd} -> BHR id {bhr_id or '(none)'}")
        elif len(records) > 1:
            count("id held by several records, left out")
            run.log("several records:", f"GND {gnd} -> BHR id {bhr_id}: {', '.join(sorted(records))}")
        else:
            s = next(iter(records))
            have = gnds.get(s, set())
            if gnd in have:
                count("record has it already")
            elif have:
                count("record has another GND number, left out")
                run.log("conflict:", f"{s} has GND {', '.join(sorted(have))}, the portal gives {gnd} (BHR id {bhr_id})")
            else:
                count("added")
                add.add((s, IRI(OWL_SAME), IRI(GND + gnd)))
    run.note(f"portal_gnd: {dict(sorted(stats.items()))}")
    return add


def generate(run):
    params = run.params
    outs = {}
    for path in run.inputs("previous"):
        if path.name not in FILES:
            continue
        name = path.name
        out = set()
        stats = {}
        for s, p, o in run.triples("previous", file=name):
            reason = None
            if params["drop_service_page"] and p == OWL_SAME and o == SERVICE_PAGE:
                reason = "sameAs the EntityFacts service page"
            elif params["drop_empty"] and p == OWL_SAME and o in EMPTY_IDS:
                reason = "sameAs with an empty identifier"
            elif params["drop_empty"] and isinstance(o, Literal) and not o.value.strip():
                reason = "empty literal"
            elif params["drop_empty"] and p == GNDID and isinstance(o, Literal) and o.value.strip() == "NA":
                reason = "GND number NA (placeholder)"
            elif params["split_mixed"] and s in MIXED and not keep_mixed(s, p, o):
                reason = "value of another record (mixed records)"
            if reason:
                stats[reason] = stats.get(reason, 0) + 1
                continue
            if params["occupation_uri"] and p == JLO + "occpation":
                p = IRI(JLO + "occupationURI")
                stats["jl:occpation as jl:occupationURI"] = stats.get("jl:occpation as jl:occupationURI", 0) + 1
            if params["portal_links"] and p == OWL_SAME and isinstance(o, IRI) and o.startswith(STEINHEIM):
                p, o = IRI(JLO + "describedAt"), IRI(PORTAL + o[len(STEINHEIM):])
                stats["BHR database link as jl:describedAt the portal page"] = \
                    stats.get("BHR database link as jl:describedAt the portal page", 0) + 1
            out.add((s, p, o))
        run.note(f"{name}: {dict(sorted(stats.items()))}")
        outs[name] = out
    if params["portal_gnd"]:
        outs["Entityfacts-bhr-sameas.ttl.gz"] |= portal_gnd(run, outs)
    for name, out in outs.items():
        run.write_turtle(name, out)

