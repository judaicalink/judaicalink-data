"""ls-geonames: every record of ours that refers to a GeoNames entry, linked to our record of the current entry (decision 0029).

References: GeoNames ids (sws.geonames.org/<id> in any form, our records data/geonames/<id>) in the stable versions of our datasets (all but geonames itself and ep); resolved
through the replacements of the dataset geonames; the rules are in jl.linksets.
"""

from jl.generator import stable_inputs
from jl.linksets import authority_linkset

LINKED = stable_inputs("linked_", exclude={"geonames", "ep", "compact-memory", "compact-memory-supp", "cm-ocr-quality",
                                           "cm-tagme", "corrections-links", "quality-annotations", "judaicalink-agents",
                                           "judaicalink-vocabulary", "ontology"}, kinds=None)
INPUTS = {"authority": "geonames/2026-10-16", **LINKED}
PARAMS = {}


def generate(run):
    links = authority_linkset(run, "geonames", "authority", LINKED, "http://data.judaicalink.org/data/geonames/")
    run.write_turtle("ls-geonames.ttl.gz", links)
