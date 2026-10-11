"""judaicalink-vocabulary: the values of the catalogue fields kind and method as SKOS concepts, from
catalog/vocabulary.toml (decision 0018). The -meta files name them as dcterms:type of a dataset.
"""

import tomllib

from jl import vocabulary
from jl.generator import GeneratorError
from jl.rdf import IRI, RDF_TYPE, Literal
from jl.turtle import PREFIXES, Namespace

INPUTS = {"vocabulary": "repo:catalog/vocabulary.toml"}
PARAMS = {}

SKOS = Namespace(PREFIXES["skos"])
OWL = Namespace(PREFIXES["owl"])
XSD = PREFIXES["xsd"]
A = IRI(RDF_TYPE)


def en(text):
    return Literal(text, lang="en")


def generate(run):
    try:
        data = vocabulary.load(run.input("vocabulary"))
    except ValueError as e:
        raise GeneratorError(str(e)) from None
    t = []
    for field in vocabulary.FIELDS:
        scheme = IRI(vocabulary.scheme_iri(field))
        f = data[field]
        t += [(scheme, A, SKOS.ConceptScheme), (scheme, SKOS.prefLabel, en(f["label"]))]
        if f.get("definition"):
            t.append((scheme, SKOS.definition, en(f["definition"])))
        derived = f.get(vocabulary.AUTOMATED)
        if derived:   # method/automated: broader concept of the automated methods, derived in the -meta
            auto = IRI(vocabulary.value_iri(field, vocabulary.AUTOMATED))
            t += [(auto, A, SKOS.Concept), (auto, SKOS.inScheme, scheme), (auto, SKOS.topConceptOf, scheme),
                  (scheme, SKOS.hasTopConcept, auto), (auto, SKOS.notation, Literal(vocabulary.AUTOMATED)),
                  (auto, SKOS.prefLabel, en(derived["label"])), (auto, SKOS.definition, en(derived["definition"])),
                  (auto, SKOS.scopeNote, en("Not used in the catalogue: stated in the metadata of every dataset "
                                            "that uses one of its narrower methods."))]
        for value, d in f["values"].items():
            c = IRI(vocabulary.value_iri(field, value))
            t += [(c, A, SKOS.Concept), (c, SKOS.inScheme, scheme), (c, SKOS.notation, Literal(value)),
                  (c, SKOS.prefLabel, en(d["label"])), (c, SKOS.definition, en(d["definition"]))]
            if derived and d.get("automated"):
                t += [(c, SKOS.broader, auto), (auto, SKOS.narrower, c)]
            else:
                t += [(c, SKOS.topConceptOf, scheme), (scheme, SKOS.hasTopConcept, c)]
            if d.get("withdrawn"):
                t += [(c, OWL.deprecated, Literal("true", XSD + "boolean")), (c, SKOS.note, en(d["withdrawn"]))]
        run.log(f"{field}: {len(f['values'])} values")
    run.write_turtle("judaicalink-vocabulary.ttl.gz", t)
