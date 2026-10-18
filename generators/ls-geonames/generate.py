"""ls-geonames: every record of ours that refers to a GeoNames entry, linked to our record of the current entry (decision 0029).

References: GeoNames ids (sws.geonames.org/<id> in any form, our records data/geonames/<id>) in our datasets and the other authority datasets (jl.authorities.linking_inputs: the stable versions, or the runs of jl generate --use); resolved
through the replacements of the dataset geonames; the rules are in jl.linksets.
"""

from jl import authorities
from jl.linksets import authority_linkset

LINKED = authorities.linking_inputs("geonames")   # our datasets and the other authority datasets
INPUTS = {"authority": authorities.authority_input("geonames"), **LINKED}
PARAMS = {}


def generate(run):
    links = authority_linkset(run, "geonames", "authority", LINKED, "http://data.judaicalink.org/data/geonames/")
    run.write_turtle("ls-geonames.ttl.gz", links)
