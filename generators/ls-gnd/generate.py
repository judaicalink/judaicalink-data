"""ls-gnd: every record of ours that refers to a GND entry, linked to our record of the current entry (decision 0029).

References: GND numbers (any IRI form of d-nb.info/gnd, our records data/gnd/<n>, gndo:gndIdentifier) in the stable versions of our datasets (all but gnd itself and ep); resolved
through the replacements of the dataset gnd; the rules are in jl.linksets.
"""

from jl.generator import stable_inputs
from jl.linksets import authority_linkset

LINKED = stable_inputs("linked_", exclude={"gnd", "ep", "compact-memory", "compact-memory-supp", "cm-ocr-quality",
                                           "cm-tagme", "corrections-links", "quality-annotations", "judaicalink-agents",
                                           "judaicalink-vocabulary", "ontology"}, kinds=None)
INPUTS = {"authority": "gnd/2026-10-16", **LINKED}
PARAMS = {}


def generate(run):
    links = authority_linkset(run, "gnd", "authority", LINKED, "http://data.judaicalink.org/data/gnd/")
    run.write_turtle("ls-gnd.ttl.gz", links)
