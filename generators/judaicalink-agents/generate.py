"""judaicalink-agents: the persons and software agents named in the -meta files, from catalog/agents.toml.

The only place where the names of persons are published as data (decision 0018); the -meta files name agents
by IRI. A withdrawn person keeps the IRI, with no name.
"""

from jl.agents import Registry, person_iri, software_iri
from jl.generator import GeneratorError
from jl.rdf import IRI, RDF_TYPE, Literal
from jl.turtle import PREFIXES, Namespace

INPUTS = {"registry": "repo:catalog/agents.toml"}
PARAMS = {}

FOAF = Namespace(PREFIXES["foaf"])
PROV = Namespace(PREFIXES["prov"])
RDFS = Namespace(PREFIXES["rdfs"])
A = IRI(RDF_TYPE)


def generate(run):
    reg = Registry(run.input("registry"))
    if reg.errors:
        raise GeneratorError("agents.toml: " + "; ".join(reg.errors))
    t = []
    for n, p in sorted(reg.persons.items()):
        s = IRI(person_iri(n))
        t.append((s, A, PROV.Person))
        if p.get("name"):
            t += [(s, A, FOAF.Person), (s, FOAF.name, Literal(p["name"]))]
            t += [(s, RDFS.seeAlso, IRI(u)) for u in p.get("links", [])]
    for name, sw in sorted(reg.software.items()):
        s = IRI(software_iri(name))
        t += [(s, A, PROV.SoftwareAgent), (s, RDFS.label, Literal(sw["label"]))]
        if sw.get("url"):
            t.append((s, FOAF.homepage, IRI(sw["url"])))
    run.log(f"{len(reg.persons)} persons, {len(reg.software)} software agents")
    run.write_turtle("judaicalink-agents.ttl.gz", t)
