"""The deterministic Turtle writer of the framework (decision 0018): same triples, same bytes.

- Prefixes come from one fixed table (PREFIXES); a file declares those it uses, sorted by name, only at the top.
- Subjects are sorted, predicates sorted with rdf:type ("a") first, objects sorted; the order is that of the
  canonical N-Triples form of the terms. One empty line between subjects.
- Literals are written in their quoted form with the datatype as given (no number shortcuts, so the lexical
  form is visible); only canonical N-Triples escapes.
- gzip with a fixed header (no file name, mtime 0).
- Optional header comments (add-version writes "# JudaicaLink dataset <slug>, version <version>" and the
  version IRI); comments are not triples.
- Blank nodes are refused (decision 0018).
"""

import gzip
import hashlib
import os
import re
from pathlib import Path

from .rdf import PN_LOCAL, RDF_TYPE, BNode, IRI, Literal, nt, nt_iri, nt_string

# The fixed prefix table. Adding a prefix changes the bytes of files written afterwards, never their triples.
PREFIXES = {
    "cc": "http://creativecommons.org/ns#",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcat": "http://www.w3.org/ns/dcat#",
    "dcterms": "http://purl.org/dc/terms/",
    "dqv": "http://www.w3.org/ns/dqv#",
    "edm": "http://www.europeana.eu/schemas/edm/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
    "geosparql": "http://www.opengis.net/ont/geosparql#",
    "gn": "https://www.geonames.org/ontology#",
    "gndo": "https://d-nb.info/standards/elementset/gnd#",
    "jl": "http://data.judaicalink.org/ontology/",
    "oa": "http://www.w3.org/ns/oa#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "prov": "http://www.w3.org/ns/prov#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "schema": "http://schema.org/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "spdx": "http://spdx.org/rdf/terms#",
    "void": "http://rdfs.org/ns/void#",
    "wd": "http://www.wikidata.org/entity/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}

# Local names are written as prefixed names where the reader's PN_LOCAL takes them as they are (no backslash
# escapes; "%XX" stays as it is in Turtle); everything else is written as a full IRI.
_LOCAL = re.compile(PN_LOCAL)
# characters that RFC 3987 does not allow in an IRI; written as \u escapes they would still be these characters
_BAD_IRI = re.compile(r'[\x00-\x20<>"{}|^`\\]')


class Namespace(str):
    """IRI factory: JL = Namespace(PREFIXES["jl"]); JL.describedAt, JL["birth-date"]."""
    __slots__ = ()

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return IRI(self + name)

    def __getitem__(self, name):
        return IRI(self + name)


class Writer:
    def __init__(self, prefixes=None):
        self.prefixes = dict(PREFIXES if prefixes is None else prefixes)
        # longest namespace first, so that the most specific prefix wins
        self.by_ns = sorted(((ns, p) for p, ns in self.prefixes.items()), key=lambda x: -len(x[0]))
        self.used = set()
        self._cache = {}

    def iri(self, iri):
        r = self._cache.get(iri)
        if r is None:
            if _BAD_IRI.search(iri):
                raise ValueError(f"not a valid IRI (percent-encode characters from source text): {iri!r}")
            r = nt_iri(iri)
            for ns, p in self.by_ns:
                if iri.startswith(ns):
                    local = iri[len(ns):]
                    if local and "\\" not in local and _LOCAL.fullmatch(local) and local.isprintable():
                        r = (p, f"{p}:{local}")
                    break
            self._cache[iri] = r
        if isinstance(r, tuple):
            self.used.add(r[0])
            return r[1]
        return r

    def term(self, t):
        if isinstance(t, Literal):
            s = nt_string(t.value)
            if t.lang:
                return f"{s}@{t.lang}"
            if t.datatype:
                return f"{s}^^{self.iri(t.datatype)}"
            return s
        if isinstance(t, BNode):
            raise ValueError(f"blank node _:{t}: the framework writes no blank nodes (decision 0018)")
        return self.iri(t)

    def body(self, triples):
        """The statements as text lines (without prefix declarations), sorted."""
        graph = {}
        for s, p, o in triples:
            if not isinstance(s, IRI) or not isinstance(p, IRI) or not isinstance(o, (IRI, Literal)):
                if isinstance(s, BNode) or isinstance(o, BNode):
                    raise ValueError("blank nodes are not written (decision 0018)")
                raise TypeError(f"not a triple of IRI/Literal terms: {(s, p, o)!r}")
            graph.setdefault(s, {}).setdefault(p, set()).add(o)
        n = 0
        out = []
        for s in sorted(graph, key=nt):
            if out:
                out.append("")
            preds = sorted(graph[s], key=lambda p: (p != RDF_TYPE, nt(p)))
            lines = []
            for p in preds:
                objs = sorted(graph[s][p], key=nt)
                n += len(objs)
                pred = "a" if p == RDF_TYPE else self.iri(p)
                terms = [self.term(o) for o in objs]
                lines.append(f"    {pred} " + (" ,\n" + " " * (len(pred) + 5)).join(terms))
            out.append(self.iri(s) + "\n" + " ;\n".join(lines) + " .")
        return out, n


def turtle_text(triples, header=(), prefixes=None):
    """(text, number of triples)."""
    w = Writer(prefixes)
    body, n = w.body(triples)
    parts = [f"# {h}" for h in header]
    if parts:
        parts.append("")
    if w.used:
        parts += [f"@prefix {p}: {nt_iri(w.prefixes[p])} ." for p in sorted(w.used)]
        parts.append("")
    parts += body
    return "\n".join(parts) + "\n", n


def write(path, triples, header=(), prefixes=None):
    """Write gzipped (".gz") or plain Turtle. Returns {path, triples, bytes, sha256}."""
    path = Path(path)
    text, n = turtle_text(triples, header, prefixes)
    data = text.encode("utf-8")
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as raw:
        if path.name.endswith(".gz"):
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as f:
                f.write(data)
        else:
            raw.write(data)
    os.replace(tmp, path)
    blob = path.read_bytes()
    return {"path": path.name, "triples": n, "bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest()}


def add_header(path, header):
    """Put header comments in front of a Turtle file written by write() (gzip or plain), deterministically.
    Returns {bytes, sha256}."""
    path = Path(path)
    gz = path.name.endswith(".gz")
    data = gzip.decompress(path.read_bytes()) if gz else path.read_bytes()
    if data.startswith(b"#"):
        raise ValueError(f"{path.name} already has a header")
    data = ("".join(f"# {h}\n" for h in header) + "\n").encode("utf-8") + data
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as raw:
        if gz:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as f:
                f.write(data)
        else:
            raw.write(data)
    os.replace(tmp, path)
    blob = path.read_bytes()
    return {"bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest()}
