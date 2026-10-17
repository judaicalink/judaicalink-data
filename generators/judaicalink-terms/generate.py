"""judaicalink-terms: a label (jl:label, English and German) for every class and property used in our datasets.

Terms: every predicate and every object of rdf:type in the stable versions (and the wikidata run, until it is a
version). Labels, per language from the first source that has one:
1. the dataset that coins the term (its vocabulary file, e.g. data/haskala/vocab/, data/bhr/vocab/);
2. the JudaicaLink ontology (its stable version: jl:label of foreign terms, rdfs:label of own terms);
3. the term's own vocabulary (rdfs:label, skos:prefLabel), read from the official file;
4. Wikidata, for its properties (wdt:, wdtn:).
A label is copied with its language tag; one without tag only if the term has neither English nor German. Terms of
the GND and GeoNames ontology are looked up under http and https, MADS/RDF under both of its namespaces.
"""

import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

from jl.generator import stable_inputs
from jl.rdf import IRI, RDF_TYPE, Literal, read_triples
from jl.turtle import PREFIXES

DATA = stable_inputs("ds_", exclude={"judaicalink-terms", "corrections-links", "compact-memory-supp"},   # no RDF data
                     add={"wikidata": "run-20261016T210958Z"})   # wikidata: becomes its version
VOCABS = {n: f"inputs:vocabularies/{n}-2026-10-17/{f}" for n, f in [
    ("gnd", "gnd.ttl"), ("agrelon", "agrelon.ttl"), ("madsrdf", "madsrdf.rdf"), ("skos", "skos.rdf"),
    ("dcterms", "dcterms.ttl"), ("dcelements", "dcelements.ttl"), ("foaf", "foaf.rdf"), ("schema", "schema.ttl"),
    ("rdf", "rdf.ttl"), ("rdfs", "rdfs.ttl"), ("owl", "owl.ttl"), ("geonames", "geonames.rdf"), ("oa", "oa.ttl"),
    ("prov", "prov.ttl"), ("bibframe", "bibframe.rdf"), ("bflc", "bflc.rdf"), ("identifiers", "identifiers.rdf"),
    ("geosparql", "geosparql.rdf"), ("dqv", "dqv.ttl")]}
INPUTS = {**DATA, **{"vocab_" + n: ref for n, ref in VOCABS.items()},
          "wikidata_properties": "inputs:web-caches/wikidata-properties-2026-10-17/properties.jsonl"}
PARAMS = {}
# our own labels for terms that no source labels (the last source)
OWN_LABELS = {"http://www.loc.gov/mads/rdf/v1#hasCharacteristic": [("characteristic", "en"), ("Merkmal", "de")]}

JL = "http://data.judaicalink.org/data/"
JLO, RDFS, SKOS = PREFIXES["jl"], PREFIXES["rdfs"], PREFIXES["skos"]
MADS = "http://www.loc.gov/mads/rdf/v1#"
LABELS = {RDFS + "label", SKOS + "prefLabel", MADS + "authoritativeLabel"}
JLLABEL = JLO + "label"
LANGS = ("en", "de")
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
XML_NS = "http://www.w3.org/XML/1998/namespace"
WIKIDATA_PROP = re.compile(r"^http://www\.wikidata\.org/prop/(?:direct|direct-normalized)/(P\d+)$")
# the same term under another namespace
ALIASES = [("http://d-nb.info/standards/elementset/gnd#", "https://d-nb.info/standards/elementset/gnd#"),
           ("http://www.loc.gov/standards/mads/rdf/v1#", "http://www.loc.gov/mads/rdf/v1#"),
           ("http://www.geonames.org/ontology#", "https://www.geonames.org/ontology#")]


def forms(term):
    yield term
    for a, b in ALIASES:
        if term.startswith(a):
            yield b + term[len(a):]
        elif term.startswith(b):
            yield a + term[len(b):]


def rdfxml_labels(path):
    """(subject, text, lang) for rdfs:label and skos:prefLabel in an RDF/XML file (typed and untyped nodes)."""
    tree = ET.parse(path)
    root = tree.getroot()
    base = root.get(f"{{{XML_NS}}}base", "")
    tags = {"{" + p.rsplit("#", 1)[0] + "#}" + p.rsplit("#", 1)[1] for p in LABELS}
    for el in root.iter():
        about = el.get(f"{{{RDF_NS}}}about")
        if about is None and el.get(f"{{{RDF_NS}}}ID") is not None:
            about = "#" + el.get(f"{{{RDF_NS}}}ID")
        if about is None:
            continue
        if about.startswith("#") or about == "":
            about = base.split("#")[0] + about
        for attr, value in el.attrib.items():   # labels given as attributes (FOAF)
            if attr in tags and value.strip():
                yield about, value.strip(), (el.get(f"{{{XML_NS}}}lang") or "").lower()
        for child in el:
            if child.tag in tags and child.text and child.text.strip():
                yield about, child.text.strip(), (child.get(f"{{{XML_NS}}}lang") or "").lower()


def triples_labels(path):
    for s, p, o in read_triples(path):
        if p in LABELS and isinstance(o, Literal) and isinstance(s, str):
            yield str(s), o.value, (o.lang or "").lower()


def generate(run):
    # 1. the terms used, and the labels the datasets give their own terms
    used, own = Counter(), defaultdict(list)
    for name in DATA:
        for s, p, o in run.triples(name):
            used[str(p)] += 1
            if p == RDF_TYPE and isinstance(o, str) and not isinstance(o, Literal):
                used[str(o)] += 1
            if p in LABELS and isinstance(o, Literal) and str(s).startswith(JL):
                own[str(s)].append((o.value, (o.lang or "").lower()))
    run.log(f"{len(used):,} terms used")

    # the sources in order: (name, {term: [(text, lang)]})
    sources = [("datasets", own)]
    onto_v = defaultdict(list)
    for s, p, o in run.triples("ds_ontology"):
        if p in (JLLABEL, RDFS + "label") and isinstance(o, Literal):
            onto_v[str(s)].append((o.value, (o.lang or "").lower()))
    sources.append(("ontology (version)", onto_v))
    for n in VOCABS:
        voc = defaultdict(list)
        path = run.input("vocab_" + n)
        rows = rdfxml_labels(path) if path.suffix == ".rdf" else triples_labels(path)
        for s, text, lang in rows:
            voc[s].append((text, lang))
        sources.append((n, voc))
    wd = {}
    with open(run.input("wikidata_properties"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            wd[r["id"]] = [(v, lang) for lang, v in sorted(r["labels"].items())]

    sources.append(("judaicalink", OWN_LABELS))

    # 2. per term and language the first source with a label
    t, by_source, none = set(), Counter(), []
    for term in sorted(used):
        found = {}
        first = None
        for name, labels in sources:
            for form in forms(term):
                for text, lang in labels.get(form, []):
                    key = lang if lang in LANGS else ("" if not lang else None)
                    if key is not None and key not in found:
                        found[key] = text
                        first = first or name
        m = WIKIDATA_PROP.match(term)
        if m:
            for text, lang in wd.get(m.group(1), []):
                if lang in LANGS and lang not in found:
                    found[lang] = text
                    first = first or "wikidata"
        if not found:
            none.append(term)
            continue
        by_source[first] += 1
        for lang in LANGS:
            if lang in found:
                t.add((IRI(term), IRI(JLLABEL), Literal(found[lang], None, lang)))
        if not any(lang in found for lang in LANGS):
            t.add((IRI(term), IRI(JLLABEL), Literal(found[""], None, None)))
    for term in none:
        run.log("no label:", term)
    run.note(f"{len(used):,} terms used; {len(used) - len(none):,} labelled, by the first source: "
             + ", ".join(f"{k} {v:,}" for k, v in by_source.most_common()) + f"; {len(none):,} without a label (log).")
    run.write_turtle("judaicalink-terms.ttl.gz", t)
