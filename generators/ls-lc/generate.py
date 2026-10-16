"""ls-lc: every record of ours that refers to a LC Name Authority File entry, linked to our record of the current entry (decision 0029).

References: LC identifiers (id.loc.gov/authorities/names/<id> and the Real World Object id.loc.gov/rwo/agents/<id>, our records data/lc/<id>) in the stable versions of our datasets (all but lc itself and ep); resolved
through the replacements of the dataset lc; the rules are in jl.linksets.
"""

from jl.generator import stable_inputs
from jl.linksets import authority_linkset

LINKED = stable_inputs("linked_", exclude={"lc", "ep", "compact-memory", "compact-memory-supp", "cm-ocr-quality",
                                           "cm-tagme", "corrections-links", "quality-annotations", "judaicalink-agents",
                                           "judaicalink-vocabulary", "ontology"}, kinds=None)
INPUTS = {"authority": "lc/2026-10-16", **LINKED}
PARAMS = {}


def generate(run):
    links = authority_linkset(run, "lc-names", "authority", LINKED, "http://data.judaicalink.org/data/lc/")
    run.write_turtle("ls-lc.ttl.gz", links)
