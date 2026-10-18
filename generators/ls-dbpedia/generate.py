"""ls-dbpedia: every record of ours that refers to an English or German Wikipedia article (or its DBpedia resource),
linked to our record of the current article (decisions 0029, 0031).

References: Wikipedia articles and DBpedia resources in any form (jl.identifiers: wikipedia-en, wikipedia-de), by
the declared identity statements of our datasets and the other authority datasets (jl.authorities.linking_inputs:
the stable versions, or the runs of jl generate --use); an old title is followed to the current article through the
replacements of the dataset dbpedia; the rules are in jl.linksets (one pass per language).
"""

from jl import authorities
from jl.linksets import authority_linkset

LINKED = authorities.linking_inputs("dbpedia")   # our datasets and the other authority datasets
INPUTS = {"authority": authorities.authority_input("dbpedia"), **LINKED}
PARAMS = {}
JL = "http://data.judaicalink.org/data/dbpedia/"


def generate(run):
    links = set()
    for source, lang in (("wikipedia-en", "en"), ("wikipedia-de", "de")):
        links |= authority_linkset(run, source, "authority", LINKED, f"{JL}{lang}/")
    run.write_turtle("ls-dbpedia.ttl.gz", links)
