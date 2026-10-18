"""lc in the cascade of the authority datasets (jl.cascade): resolve and links from an index of the LC dump.

The index (built once per dump, in <build>/_index/): the record identifiers of the LC Name Authority File (blocks
"# BEGIN /authorities/names/<id>"), the deprecated ones (madsrdf:DeprecatedAuthority; LC states no successor, so they
have no current identifier), and per record the madsrdf:hasExactExternalAuthority targets of the authority and its
Real World Object, as the dataset lc writes them (Wikidata pages as items, canonical forms, without JudaicaLink).
"""

import gzip
import re
import sqlite3

from jl import identifiers
from jl.cascade import index_path, static_seeds
from jl.generator import load_shared, resolve
from jl.iris import canonical

gen = load_shared("lc", "generate")

EXACT = gen.MADS + "hasExactExternalAuthority"
LINE = re.compile(r"^<http://id\.loc\.gov/(?:authorities/names|rwo/agents)/(" + gen.LC_ID + r")> <" + re.escape(EXACT)
                  + r"> <([^>]*)> \.")


class Lookup:
    sources = ("lc-names",)
    searched_by = ()

    def __init__(self, cfg, cat, log):
        self.cfg, self.cat = cfg, cat
        f = resolve(cfg, cat, gen.INPUTS["names"])[0]
        self.db = sqlite3.connect(index_path(cfg, "lc", f["sha256"], self.build, f["path"], log))

    @staticmethod
    def build(db, dump, log):
        db.execute("CREATE TABLE records (id TEXT PRIMARY KEY, deprecated INTEGER) WITHOUT ROWID")
        db.execute("CREATE TABLE links (id TEXT, target TEXT)")
        recs, links, n = [], [], 0
        current, deprecated = None, False
        with gzip.open(dump, "rt", encoding="utf-8") as f:
            for line in f:
                if line.startswith("# BEGIN"):
                    m = gen.BEGIN.match(line)
                    current, deprecated = (m.group(1) if m else None), False
                elif line.startswith("# END"):
                    if current:
                        recs.append((current, 1 if deprecated else 0))
                        n += 1
                    current = None
                elif current:
                    if gen.MADS + "DeprecatedAuthority>" in line:
                        deprecated = True
                    elif EXACT in line:
                        m = LINE.match(line)
                        if m and m.group(1) == current:
                            x = canonical(gen.wikidata_page(m.group(2)))
                            if not identifiers.is_ours(x):
                                links.append((current, x))
                if len(recs) >= 500_000:
                    db.executemany("INSERT OR IGNORE INTO records VALUES (?, ?)", recs)
                    recs = []
                if len(links) >= 500_000:
                    db.executemany("INSERT INTO links VALUES (?, ?)", links)
                    links = []
        db.executemany("INSERT OR IGNORE INTO records VALUES (?, ?)", recs)
        db.executemany("INSERT INTO links VALUES (?, ?)", links)
        db.execute("CREATE INDEX links_id ON links (id)")
        log(f"  lc index: {n:,} records")

    def seeds(self):
        return static_seeds(self.cfg, self.cat, "lc")

    def resolve(self, source, ids):
        out = {}
        for i in ids:
            row = self.db.execute("SELECT deprecated FROM records WHERE id = ?", (i,)).fetchone()
            out[i] = i if row and not row[0] else None   # deprecated (no successor stated) or not in the dump
        return out

    def links(self, source, ids):
        out = {}
        for i in ids:
            ls = set()
            for (target,) in self.db.execute("SELECT target FROM links WHERE id = ?", (i,)):
                x = identifiers.identify(target)
                if x:
                    ls.add((EXACT, x[0], x[1]))
            out[i] = ls
        return out
