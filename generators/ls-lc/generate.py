"""ls-lc: every record of ours that refers to a LC Name Authority File entry, linked to our record of the current entry (decision 0029).

References: LC identifiers (id.loc.gov/authorities/names/<id> and the Real World Object id.loc.gov/rwo/agents/<id>, our records data/lc/<id>) in our datasets and the other authority datasets (jl.authorities.linking_inputs: the stable versions, or the runs of jl generate --use); resolved
through the replacements of the dataset lc; the rules are in jl.linksets.
"""

from jl import authorities
from jl.linksets import authority_linkset

LINKED = authorities.linking_inputs("lc")   # our datasets and the other authority datasets
INPUTS = {"authority": authorities.authority_input("lc"), **LINKED}
PARAMS = {}


def generate(run):
    links = authority_linkset(run, "lc-names", "authority", LINKED, "http://data.judaicalink.org/data/lc/")
    run.write_turtle("ls-lc.ttl.gz", links)
