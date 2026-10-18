"""geonames in the cascade of the authority datasets (jl.cascade): resolve and links from an index of the GeoNames dump.

The index (built once per dump, in <build>/_index/): the feature ids of allCountries.txt, and per feature the
Wikidata items of its alternate names of the kind 'wkdt' (as generate.py takes them). An id not in the dump has no
current feature (GeoNames publishes no merged or deleted features).
"""

import re
import sqlite3

from jl.cascade import index_path, static_seeds
from jl.generator import load_shared, resolve

gen = load_shared("geonames", "generate")

SAME = "http://www.w3.org/2002/07/owl#sameAs"
QID = re.compile(r"Q[0-9]+")


class Lookup:
    sources = ("geonames",)
    searched_by = ()

    def __init__(self, cfg, cat, log):
        self.cfg, self.cat = cfg, cat
        files = {k: resolve(cfg, cat, gen.INPUTS[k])[0] for k in ("all", "alternate")}
        key = files["all"]["sha256"][:8] + files["alternate"]["sha256"][:8]
        self.paths = {k: f["path"] for k, f in files.items()}
        self.db = sqlite3.connect(index_path(cfg, "geonames", key, self.build, files["all"]["path"], log))

    def build(self, db, _all, log):
        db.execute("CREATE TABLE features (id TEXT PRIMARY KEY) WITHOUT ROWID")
        db.execute("CREATE TABLE wkdt (id TEXT, item TEXT)")
        batch = []
        for line in gen.lines(self.paths["all"], "allCountries.txt"):
            batch.append((line.split("\t", 1)[0],))
            if len(batch) >= 1_000_000:
                db.executemany("INSERT OR IGNORE INTO features VALUES (?)", batch)
                batch = []
        db.executemany("INSERT OR IGNORE INTO features VALUES (?)", batch)
        log("  geonames index: features done")
        batch = []
        for line in gen.lines(self.paths["alternate"], "alternateNamesV2.txt"):
            c = line.split("\t", 4)
            if len(c) > 3 and c[2] == "wkdt" and QID.fullmatch(c[3]):
                batch.append((c[1], c[3]))
        db.executemany("INSERT INTO wkdt VALUES (?, ?)", batch)
        db.execute("CREATE INDEX wkdt_id ON wkdt (id)")

    def seeds(self):
        return static_seeds(self.cfg, self.cat, "geonames")

    def resolve(self, source, ids):
        return {i: i if self.db.execute("SELECT 1 FROM features WHERE id = ?", (i,)).fetchone() else None
                for i in ids}

    def links(self, source, ids):
        return {i: {(SAME, "wikidata", q) for (q,) in self.db.execute("SELECT item FROM wkdt WHERE id = ?", (i,))}
                for i in ids}
