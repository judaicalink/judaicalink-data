"""ls-gnd: every record of ours that refers to a GND entry, linked to our record of the current entry (decision 0029).

References: GND numbers (any IRI form of d-nb.info/gnd, our records data/gnd/<n>, gndo:gndIdentifier) in our datasets and the other authority datasets (jl.authorities.linking_inputs: the stable versions, or the runs of jl generate --use); resolved
through the replacements of the dataset gnd; the rules are in jl.linksets.
"""

from jl import authorities
from jl.linksets import authority_linkset

LINKED = authorities.linking_inputs("gnd")   # our datasets and the other authority datasets
INPUTS = {"authority": authorities.authority_input("gnd"), **LINKED}
PARAMS = {}


def generate(run):
    links = authority_linkset(run, "gnd", "authority", LINKED, "http://data.judaicalink.org/data/gnd/")
    run.write_turtle("ls-gnd.ttl.gz", links)
