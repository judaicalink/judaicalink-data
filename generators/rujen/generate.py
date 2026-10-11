"""rujen: the Encyclopedia of Russian Jewry (rujen.ru), from the crawl of 2020-09-28.

Transformation only: the RDF step of judaicalink-labs `1ac14f1` (`create_rdf`, `local`, `get_latin_string` in
original/judaicalink-labs@1ac14f1/.../generate_rujen.py), ported to the framework without changes to its logic,
including its quirks (the doubled "/index.php//index.php/" in jl:describedAt). The crawl (acquisition with
Scrapy and BeautifulSoup) is the input, one JSON object per page; it is published with the version.
"""

import gzip
import json
import re
from urllib.parse import unquote

from jl.rdf import IRI, RDF_TYPE, Literal
from jl.turtle import PREFIXES, Namespace

INPUTS = {"crawl": "rujen/2020-09-28/rujen.jsonl.gz"}
PARAMS = {}

JLO = Namespace(PREFIXES["jl"])
SKOS = Namespace(PREFIXES["skos"])
DCTERMS = Namespace(PREFIXES["dcterms"])
TYPE = IRI(RDF_TYPE)

LATIN = ["a", "b", "v", "g", "d", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f",
         "kh", "ts", "ch", "sh", "shch", "j", "y", "j", "e", "yu", "ya", "e", "e"]
CYRILLIC_A = 1072   # "а"


def latin(cyrillic):
    out = ""
    for char in cyrillic.lower():
        n = ord(char) - CYRILLIC_A
        out += LATIN[n] if 0 <= n < 34 else char
    return out


def local(uri):
    if "index.php" in uri:
        return IRI("http://data.judaicalink.org/data/rujen/" + latin(unquote(uri).replace("/index.php/", "")))
    return IRI(uri)


def page_triples(d, log):
    subject = local(d["uri"])
    t = [(subject, TYPE, SKOS.Concept),
         (subject, SKOS.prefLabel, Literal(d["title"])),
         (subject, JLO.describedAt, IRI(f"http://rujen.ru/index.php/{d['uri']}"))]
    identifier = unquote(d["uri"].replace("/index.php/", ""))
    t.append((subject, DCTERMS.identifier, Literal(identifier)))
    for link in d["links"]:
        t.append((subject, SKOS.related, local(link["href"])))
        if len(link["text"]) > 0:
            t.append((local(link["href"]), SKOS.altLabel, Literal(link["text"])))
    for cat in d.get("categories", []):
        if cat == "Персоналии":
            t.append((subject, TYPE, JLO.Person))
        elif cat == "География":
            t.append((subject, TYPE, JLO.Place))
        else:
            log("Unknown category: " + cat)
    if "abstract" in d:
        t.append((subject, JLO.hasAbstract, Literal(d["abstract"], None, "ru")))
        refer = re.search(r"^(.+), см\. (\S+)\.$", d["abstract"])
        if refer:
            source, target = refer.group(1), refer.group(2)
            target_check = False
            for link in d.get("links", []):
                if f"/{unquote(target).lower()}" in unquote(link["href"]).lower():
                    target_check = link["href"]
            source_check = identifier == source.lower().replace(" ", "_")
            if not source_check or not target_check:
                log(f"{source} -> {target} ({identifier}<>{source.lower().replace(' ', '_')}) ({target_check})")
            else:
                t.append((subject, JLO.referTo, local(target_check)))
    else:
        t.append((subject, SKOS.scopeNote,
                  Literal("The article describing this concept does not (yet) exist in the encyclopedia.", None, "en")))
    return t


def generate(run):
    triples = []
    with gzip.open(run.input("crawl"), "rt", encoding="utf-8") as f:
        for line in f:
            triples += page_triples(json.loads(line), run.log)
    run.write_turtle("rujen.ttl.gz", triples)
    run.copy_input("crawl")
