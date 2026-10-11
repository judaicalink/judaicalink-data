"""stolpersteine: the persons of the Stolpersteine in Mainz, from the crawl of the Wikipedia lists.

Transformation only: the RDF step of judaicalink-labs `4a9e253` (`create_rdf` in
original/judaicalink-labs@4a9e253/.../generate_stolpersteine.py), ported to the framework without changes to
its logic. The crawl (acquisition with Scrapy and BeautifulSoup, 2020-10-06) is the input; each line holds the
lists that the spider extracted from one Wikipedia page. The crawl is published with the version.
"""

import gzip
import json

from jl.rdf import IRI, RDF_TYPE, Literal
from jl.turtle import PREFIXES, Namespace

INPUTS = {"crawl": "stolpersteine/2020-10-06/stolpersteine.jsonl.gz"}
PARAMS = {}

JLO = Namespace(PREFIXES["jl"])
FOAF = Namespace(PREFIXES["foaf"])
SKOS = Namespace(PREFIXES["skos"])
DC = Namespace(PREFIXES["dc"])
DATA = "http://data.judaicalink.org/data/stolpersteine/"
LIST = IRI("https://de.wikipedia.org/wiki/Liste_der_Stolpersteine_in_Mainz")


def person(triples, uri, name, stonetext, picurl, nameremark, remarks):
    s = IRI(uri)
    triples += [(s, IRI(RDF_TYPE), FOAF.Person),
                (s, SKOS.prefLabel, Literal(name.title())),
                (s, JLO.hasAbstract, Literal(stonetext.title())),
                (s, DC.subject, IRI(picurl)),
                (s, FOAF.primaryTopic, LIST)]
    for remark in remarks:
        if nameremark.title() in remark:
            triples.append((s, SKOS.scopeNote, Literal(remark)))


def page_triples(d):
    """The triples of one crawled page; the two loops of create_rdf (name forms 'First_Last', 'Last_First')."""
    triples = []
    for links in (d["namelinklist1"], d["namelinklist2"]):
        for i in range(len(links)):
            for picurl in d["picurllist"]:
                if links[i].lower() in picurl.lower():
                    person(triples, DATA + links[i].title(), d["namelist"][i], d["stonetextlist"][i], picurl,
                           d["namelistremarks"][i], d["remarktextlist"])
    return triples


def generate(run):
    triples = []
    with gzip.open(run.input("crawl"), "rt", encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            t = page_triples(json.loads(line))
            run.log(f"page {n}: {len(t)} statements")
            triples += t
    run.write_turtle("stolpersteine.ttl.gz", triples)
    run.copy_input("crawl")
