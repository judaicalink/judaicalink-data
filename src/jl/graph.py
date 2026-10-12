"""The framework's index of RDF inputs (decision 0018): the declared input files in memory, triple patterns.

    g = Graph.load([path, ...])
    g.objects(s, p)          # objects of a subject and predicate
    g.subjects(p, o)         # subjects with a predicate and object
    g.value(s, p)            # the one object, None if there is none, an error if there are several
    g.triples(s, p, o)       # any pattern; None is a wildcard
    g.predicates(s)          # predicates of a subject

Terms as in rdf.py (IRI, Literal, BNode), exactly as in the files. Duplicates are kept once. Results come in
the order in which the triples were read (file order), never in hash order, so they are the same for the same
inputs. Joins are written in Python; generators sort what they write (0011).
"""

from .corrections import key
from .rdf import read_triples


class Graph:
    def __init__(self):
        self._spo = {}     # s -> p -> {o: None}; dicts as ordered sets
        self._pos = None   # p -> o -> {s: None}, built on first use
        self._terms = {}   # interning: one object per distinct term
        self.files = []    # [{path, statements, triples, rdf_star}]
        self.size = 0

    @classmethod
    def load(cls, paths, skip=None):
        """skip: a set of triple keys (corrections.key) to leave out, the deletions of the corrections (0023)."""
        g = cls()
        for p in paths:
            g.add_file(p, skip)
        return g

    def _term(self, t):
        return self._terms.setdefault(t, t)

    def add(self, s, p, o):
        """Add a triple; returns True if it was new."""
        s, p, o = self._term(s), self._term(p), self._term(o)
        objs = self._spo.setdefault(s, {}).setdefault(p, {})
        if o in objs:
            return False
        objs[o] = None
        self.size += 1
        if self._pos is not None:
            self._pos.setdefault(p, {}).setdefault(o, {})[s] = None
        return True

    def add_file(self, path, skip=None):
        report, n, new, skipped = {}, 0, 0, 0
        for t in read_triples(path, report):
            n += 1
            if skip and key(t) in skip:
                skipped += 1
                continue
            new += self.add(*t)
        self.files.append({"path": str(path), "statements": n, "new_triples": new,
                           "rdf_star": report.get("rdf_star", 0), "deleted_by_corrections": skipped})

    def __len__(self):
        return self.size

    def __contains__(self, triple):
        s, p, o = triple
        return o in self._spo.get(s, {}).get(p, {})

    def _by_po(self):
        if self._pos is None:
            pos = {}
            for s, preds in self._spo.items():
                for p, objs in preds.items():
                    for o in objs:
                        pos.setdefault(p, {}).setdefault(o, {})[s] = None
            self._pos = pos
        return self._pos

    def subjects_all(self):
        return list(self._spo)

    def predicates(self, s):
        return list(self._spo.get(s, {}))

    def objects(self, s, p):
        return list(self._spo.get(s, {}).get(p, {}))

    def subjects(self, p, o):
        return list(self._by_po().get(p, {}).get(o, {}))

    def value(self, s, p):
        objs = self.objects(s, p)
        if len(objs) > 1:
            raise ValueError(f"{s} {p}: {len(objs)} values")
        return objs[0] if objs else None

    def triples(self, s=None, p=None, o=None):
        """All triples matching the pattern (None = any), in file order."""
        if s is not None:
            preds = self._spo.get(s, {})
            for p2 in ([p] if p is not None else list(preds)):
                objs = preds.get(p2, {})
                if o is not None:
                    if o in objs:
                        yield s, p2, o
                else:
                    for o2 in objs:
                        yield s, p2, o2
            return
        if p is not None:
            by_o = self._by_po().get(p, {})
            for o2 in ([o] if o is not None else list(by_o)):
                for s2 in by_o.get(o2, {}):
                    yield s2, p, o2
            return
        for s2, preds in self._spo.items():
            for p2, objs in preds.items():
                if o is None:
                    for o2 in objs:
                        yield s2, p2, o2
                elif o in objs:
                    yield s2, p2, o
