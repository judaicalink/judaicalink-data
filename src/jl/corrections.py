"""Correction datasets (decision 0023): kind `correction`. The additions are the data of the dataset, in its own graph;
the deletions are a SPARQL 1.1 Update file <slug>-deletions.ru.gz that removes triples from every graph that contains
them. Corrections are applied after all other datasets; among them the order does not matter (no correction adds a
triple that another deletes).

The deletions file always has this form (prefixes and comments allowed, only explicit triples, no blank nodes):

    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    DELETE { GRAPH ?g { ?s ?p ?o } }
    WHERE {
      VALUES (?s ?p ?o) {
        # why
        (<http://data.judaicalink.org/data/bhr/X> owl:sameAs <http://example.org/page>)
      }
      GRAPH ?g { ?s ?p ?o }
    }

Generators read their inputs with the deletions of the stable correction versions applied (generator.py).
"""

import gzip
import io
import os
import re
from pathlib import Path

from . import rdf
from .rdf import XSD_STRING, BNode, Literal, ParseError
from .turtle import Writer, nt_iri

SUFFIX = "-deletions.ru.gz"
KIND = "correction"

_TOKENS = re.compile(rdf._TOKENS.pattern.replace(
    r"(?P<punct>[.;,\[\]()])", r"(?P<var>\?[A-Za-z_][A-Za-z0-9_]*)|(?P<brace>[{}])|(?P<punct>[.;,\[\]()])"), re.S)


def is_deletions(path):
    return Path(path).name.endswith(SUFFIX)


def key(triple):
    """A triple as a set key: literals compared as RDF 1.1 does (xsd:string = simple literal, language tags in any
    case)."""
    return tuple(Literal(t.value, None if t.datatype == XSD_STRING else t.datatype, t.lang.lower() if t.lang else None)
                 if isinstance(t, Literal) else t for t in triple)


class DeletionsParser(rdf.TurtleParser):
    TOKENS = _TOKENS

    def word(self, w):
        k, v = self.next_token()
        if k != "word" or v.upper() != w:
            self.error(f"expected {w}, found {v!r} (decision 0023: one fixed form)")

    def var(self, name):
        if self.next_token() != ("var", "?" + name):
            self.error(f"expected ?{name} (decision 0023: one fixed form)")

    def pattern(self):
        self.expect("{")
        for v in ("s", "p", "o"):
            self.var(v)
        self.expect("}")

    def rows(self):
        while self.peek()[0] == "word" and self.peek()[1].upper() == "PREFIX":
            self.next_token()
            self.directive("prefix")
        self.word("DELETE")
        self.expect("{")
        self.word("GRAPH")
        self.var("g")
        self.pattern()
        self.expect("}")
        self.word("WHERE")
        self.expect("{")
        self.word("VALUES")
        self.expect("(")
        for v in ("s", "p", "o"):
            self.var(v)
        self.expect(")")
        self.expect("{")
        while self.peek() != ("brace", "}"):
            self.expect("(")
            s = self.term(self.next_token(), "subject")
            p = self.term(self.next_token(), "predicate")
            o = self.term(self.next_token(), "object")
            self.expect(")")
            if isinstance(s, BNode) or isinstance(o, BNode):
                self.error("blank nodes cannot be deleted (decision 0023)")
            yield (s, p, o)
        self.expect("}")
        self.word("GRAPH")
        self.var("g")
        self.pattern()
        self.expect("}")
        if self.peek()[1] == ";":
            self.next_token()
        if self.peek()[0] != "eof":
            self.error(f"unexpected {self.peek()[1]!r} after the operation (decision 0023: one operation)")


def read(path):
    """The triples a deletions file deletes, in file order."""
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return list(DeletionsParser(f, Path(path).name).rows())


def text(blocks, prefixes=None):
    """The deletions file for blocks [(comment lines, triples)]: rows sorted within a block, blocks in the order
    given, prefixes only where used."""
    w = Writer(prefixes)
    body = []
    for comments, triples in blocks:
        rows = sorted((w.term(s), w.term(p), w.term(o)) for s, p, o in set(triples))
        if body:
            body.append("")
        body += [f"  # {c}" for c in comments]
        body += [f"  ({s} {p} {o})" for s, p, o in rows]
    lines = [f"PREFIX {p}: {nt_iri(w.prefixes[p])}" for p in sorted(w.used)]
    lines += ["DELETE { GRAPH ?g { ?s ?p ?o } }", "WHERE {", "  VALUES (?s ?p ?o) {"]
    lines += ["  " + b if b else "" for b in body]
    lines += ["  }", "  GRAPH ?g { ?s ?p ?o }", "}"]
    return "\n".join(lines) + "\n"


def write(path, blocks, prefixes=None):
    """Write a deletions file (gzip, deterministic). Returns {path, deletions, bytes}."""
    path = Path(path)
    data = text(blocks, prefixes).encode("utf-8")
    n = len(list(DeletionsParser(io.StringIO(data.decode("utf-8")), path.name).rows()))   # checks the form
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as f:
            f.write(data)
    os.replace(tmp, path)
    return {"path": path.name, "deletions": n, "bytes": path.stat().st_size}


def stable_deletions(cat, store=None, exclude=()):
    """The deletions files of the stable versions of all correction datasets: [(slug, version, path, local path or
    None)]."""
    out = []
    for slug, e in sorted(cat.entries.items()):
        if e.data.get("kind") != KIND or slug in exclude or not e.stable:
            continue
        for f in (e.version(e.stable) or {}).get("files", []):
            if isinstance(f, dict) and is_deletions(f["path"]):
                out.append((slug, e.stable, f["path"], Path(store) / slug / e.stable / f["path"] if store else None))
    return out




def check(cat, store, out=print):
    """Check the stable correction versions against the stable versions of all other datasets: every deleted triple
    is in some dataset (stale ones are reported), no correction adds a triple another deletes; and which datasets each
    correction concerns (derived). Returns (corrections, stale deletions, conflicts)."""
    from .generator import is_meta
    dels = {}   # correction slug -> {key: triple}
    for slug, _v, _p, local in stable_deletions(cat, store):
        dels.setdefault(slug, {}).update({key(t): t for t in read(local)})
    if not dels:
        out("no stable correction versions with deletions")
        return 0, 0, 0
    wanted = {}
    for slug, ks in dels.items():
        for k in ks:
            wanted.setdefault(k, set()).add(slug)
    found = {}   # key -> datasets containing it
    conflicts = 0
    for slug, e in sorted(cat.entries.items()):
        if not e.stable:
            continue
        for f in (e.version(e.stable) or {}).get("files", []):
            if not isinstance(f, dict) or is_meta(f["path"]) or not rdf.rdf_format(f["path"]):
                continue
            for t in rdf.read_triples(Path(store) / slug / e.stable / f["path"]):
                k = key(t)
                if k in wanted:
                    if e.data.get("kind") == KIND:
                        conflicts += 1
                        out(f"conflict: {slug} adds a triple that {', '.join(sorted(wanted[k]))} deletes: {t}")
                    else:
                        found.setdefault(k, set()).add(slug)
    stale = 0
    for slug, ks in sorted(dels.items()):
        concerns = {}
        for k in ks:
            for d in found.get(k, ()):
                concerns[d] = concerns.get(d, 0) + 1
        missing = [ks[k] for k in ks if k not in found]
        stale += len(missing)
        out(f"{slug}: {len(ks):,} deletions; concerns " + (", ".join(f"{d} ({n:,})" for d, n in sorted(concerns.items()))
                                                         or "no dataset") + (f"; {len(missing):,} stale" if missing else ""))
        for t in missing[:20]:
            out(f"  stale (in no stable version): {t}")
    return len(dels), stale, conflicts
