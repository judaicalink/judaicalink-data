"""The YIVO articles and their Wikidata items (P8569), shared by ls-yivo-wikidata and record-classes.

An article is identified by the name in its jl:describedAt address (yivoencyclopedia.org/article.aspx/<name>), which
is the value of P8569; compared by key(): without case (yivo lower-cased its IRIs in 2020, Wikidata keeps the case of
the site), accents, and with spaces, commas and hyphens as underscores (Wikidata has "Otsar ha-Sifrut",
"Teller, Yisakhar Ber", "Łódź" for the articles Otsar_ha-Sifrut, Teller_Yisakhar_Ber, Łodz).
"""

import re
import unicodedata
import urllib.parse
from collections import defaultdict

from jl.rdf import Literal

ARTICLE = "article.aspx/"
WD = "http://www.wikidata.org/entity/"

# upper classes of classes-top.rq, by the class they stand for in JudaicaLink
UPPER = {"Place": {"Q2221906", "Q56061", "Q486972"}, "Organization": {"Q43229"},
         "Work": {"Q47461344", "Q1002697", "Q17537576"}}


def key(name):
    s = "".join(ch for ch in unicodedata.normalize("NFKD", name) if not unicodedata.combining(ch)).lower()
    return re.sub(r"[\s,_-]+", "_", s).strip("_")


def articles(triples):
    """{key of the article name: the yivo record IRI}, from the jl:describedAt links of yivo."""
    out = {}
    for s, p, o in triples:
        if p.endswith("/describedAt"):
            v = o.value if isinstance(o, Literal) else str(o)
            if ARTICLE in v:
                out[key(urllib.parse.unquote(v.split(ARTICLE, 1)[1]))] = s
    return out


def qid(cell):
    return cell.strip().strip("<>").rsplit("/", 1)[-1]


def read_tsv(path):
    with open(path, encoding="utf-8") as f:
        rows = [line.rstrip("\n").split("\t") for line in f]
    return rows[1:]


def items(path):
    """{key of the article name: {Q-ids}}, {Q-id: {class Q-ids}} from p8569.tsv."""
    by_name, classes = defaultdict(set), defaultdict(set)
    for row in read_tsv(path):
        item, name, cls = (row + ["", ""])[:3]
        name = name.strip()
        if name.startswith('"'):
            name = name[1:name.rindex('"')]
        q = qid(item)
        by_name[key(name)].add(q)
        if cls.strip():
            classes[q].add(qid(cls))
    return by_name, classes


def uppers(path):
    """{class Q-id: {upper class Q-ids}} from classes-top.tsv."""
    out = defaultdict(set)
    for row in read_tsv(path):
        out[qid(row[0])].add(qid(row[1]))
    return out


def wikidata_class(qids, classes, upper):
    """Person, Place, Organization, Work, or None, from the classes of the items (in this order)."""
    cs = {c for q in qids for c in classes.get(q, ())}
    if "Q5" in cs:
        return "Person"
    tops = {t for c in cs for t in upper.get(c, ())}
    for name in ("Place", "Organization", "Work"):
        if tops & UPPER[name]:
            return name
    return None
