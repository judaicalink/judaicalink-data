"""sosy: a new version made from the version 2022-07-07 with one systematic error fixed (decision 0024).

The source (the Soundscape Synagoge API) answers 401 since, so this generator transforms the previous version. Fix
(parameter occupation_iris, default on): 204 values of jl:occupation are the addresses of HTML views
(https://data.judaicalink.org/data/html/occupation/<name>); they become the occupation IRIs
http://data.judaicalink.org/data/occupation/<name> (all 27 are used by gnd-persons), stated with jl:occupationURI,
the property for occupation IRIs (0020). The occupations given as text stay. With the fix off, the output has the same
triples as 2022-07-07.
"""

from jl.rdf import IRI, Literal
from jl.turtle import PREFIXES

INPUTS = {"previous": "sosy/2022-07-07"}
PARAMS = {"occupation_iris": True}

JLO = PREFIXES["jl"]
HTML_VIEW = "https://data.judaicalink.org/data/html/occupation/"
OCCUPATION = "http://data.judaicalink.org/data/occupation/"


def generate(run):
    out, n = set(), 0
    for s, p, o in run.triples("previous", file="sosy-final-01.ttl.gz"):
        if run.params["occupation_iris"] and p == JLO + "occupation" and not isinstance(o, Literal) \
                and o.startswith(HTML_VIEW):
            p, o = IRI(JLO + "occupationURI"), IRI(OCCUPATION + o[len(HTML_VIEW):])
            n += 1
        out.add((s, p, o))
    run.note(f"{n} addresses of HTML views as occupation IRIs (jl:occupationURI).")
    run.write_turtle("sosy-final-01.ttl.gz", out)
