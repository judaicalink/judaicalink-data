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
"""

from jl.rdf import IRI, Literal
from jl.turtle import PREFIXES

INPUTS = {"previous": "bhr/2018-10-24"}
PARAMS = {"drop_service_page": True, "drop_empty": True, "split_mixed": True, "occupation_uri": True}

JLO = PREFIXES["jl"]
OWL_SAME = PREFIXES["owl"] + "sameAs"
GNDID = "http://d-nb.info/standards/elementset/gnd#gndIdentifier"
BHR = "http://data.judaicalink.org/data/bhr/"
SERVICE_PAGE = "http://www.dnb.de/DE/Service/DigitaleDienste/EntityFacts/entityfacts_node.html"
EMPTY_IDS = {"http://d-nb.info/gnd//", "http://hub.culturegraph.org/entityfacts//",
             "http://www.steinheim-institut.de/see-also/query.html?kategorie1=GND&text1=/"}
STEINHEIM = "http://steinheim-institut.de:50580/cgi-bin/bhr?id="
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


def generate(run):
    params = run.params
    for path in run.inputs("previous"):
        if path.name not in FILES:
            continue
        out = set()
        stats = {}
        for s, p, o in run.triples("previous", file=path.name):
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
            out.add((s, p, o))
        run.note(f"{path.name}: {dict(sorted(stats.items()))}")
        run.write_turtle(path.name, out)

