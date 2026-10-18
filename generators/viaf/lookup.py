"""viaf in the cascade of the authority datasets (jl.cascade): resolve and links from an index of the VIAF dump.

The index (built once per dump, in <build>/_index/): the clusters of the dump and their schema:sameAs targets (the
records of other sources). A number not in the dump has no current cluster (the dump states no merged clusters).
"""

import gzip
import re
import sqlite3

from jl import identifiers
from jl.cascade import index_path, static_seeds
from jl.generator import load_shared, resolve
from jl.iris import canonical
from jl.rdf import unescape_string

gen = load_shared("viaf", "generate")

SAME = "http://www.w3.org/2002/07/owl#sameAs"   # the dataset writes VIAF's schema:sameAs as owl:sameAs
LINE = re.compile(r"^<http://viaf\.org/viaf/([0-9]+)> <([^>]+)> <([^>]*)> \.")


class Lookup:
    sources = ("viaf",)
    searched_by = ()

    def __init__(self, cfg, cat, log):
        f = resolve(cfg, cat, gen.INPUTS["dump"])[0]
        self.cfg, self.cat = cfg, cat
        self.db = sqlite3.connect(index_path(cfg, "viaf", f["sha256"], self.build, f["path"], log))

    @staticmethod
    def build(db, dump, log):
        db.execute("CREATE TABLE clusters (id TEXT PRIMARY KEY) WITHOUT ROWID")
        db.execute("CREATE TABLE links (id TEXT, target TEXT)")
        ids, links, last, n = [], [], None, 0
        with gzip.open(dump, "rt", encoding="utf-8", errors="replace") as f:
            for line in f:
                n += 1
                if not line.startswith("<http://viaf.org/viaf/"):
                    continue
                k = line[22:line.find(">")]
                if not k.isdigit():
                    continue   # documents, source records, works
                if k != last:
                    ids.append((k,))
                    last = k
                m = LINE.match(line)
                if m and m.group(2) == gen.SCHEMA + "sameAs" and not gen.NO_PATH.match(m.group(3)):
                    links.append((k, canonical(unescape_string(m.group(3)))))   # \u escapes, as the generator reads them
                if len(ids) >= 1_000_000:
                    db.executemany("INSERT OR IGNORE INTO clusters VALUES (?)", ids)
                    ids = []
                if len(links) >= 1_000_000:
                    db.executemany("INSERT INTO links VALUES (?, ?)", links)
                    links = []
                if n % 100_000_000 == 0:
                    log(f"  viaf index: {n:,} lines")
        db.executemany("INSERT OR IGNORE INTO clusters VALUES (?)", ids)
        db.executemany("INSERT INTO links VALUES (?, ?)", links)
        db.execute("CREATE INDEX links_id ON links (id)")

    def seeds(self):
        return static_seeds(self.cfg, self.cat, "viaf")

    def resolve(self, source, ids):
        out = {}
        for i in ids:
            out[i] = i if self.db.execute("SELECT 1 FROM clusters WHERE id = ?", (i,)).fetchone() else None
        return out

    def links(self, source, ids):
        out = {}
        for i in ids:
            ls = set()
            for (target,) in self.db.execute("SELECT target FROM links WHERE id = ?", (i,)):
                x = identifiers.identify(target)
                if x:
                    ls.add((SAME, x[0], x[1]))
            out[i] = ls
        return out
