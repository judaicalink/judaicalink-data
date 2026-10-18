"""gnd in the cascade of the authority datasets (jl.cascade): resolve and links from an index of the GND dumps.

The index (built once per set of inputs, in <build>/_index/): the GND numbers that are records of the LDS dump, the
former numbers of these records (dnb:deprecatedUri, owl:sameAs to another GND number, as generate.py reads them) and
the redirects and deletions of the redirect file (chains followed), and per number the EntityFacts sameAs targets as
the dataset gnd writes them (owl:sameAs; without [ID] placeholders, the GND itself and JudaicaLink).
The static lists of generate.py are its seeds: freimann, ubffm-authors, previous (gnd-persons 2018).
"""

import csv
import gzip
import hashlib
import json
import re
import sqlite3

from jl import identifiers
from jl.cascade import index_path, static_seeds
from jl.generator import load_shared, resolve
from jl.iris import canonical

gen = load_shared("gnd", "generate")

SAME = "http://www.w3.org/2002/07/owl#sameAs"
FIRST_ID = re.compile(r'"@id"\s*:\s*"https://d-nb\.info/gnd/(' + gen.NUMBER + ')"')


class Lookup:
    sources = ("gnd",)
    searched_by = ()

    def __init__(self, cfg, cat, log):
        self.cfg, self.cat = cfg, cat
        self.files = {k: resolve(cfg, cat, gen.INPUTS[k])[0] for k in ("lds", "entityfacts", "redirects")}
        key = hashlib.sha256("".join(self.files[k]["sha256"] for k in ("lds", "entityfacts", "redirects"))
                             .encode()).hexdigest()
        self.db = sqlite3.connect(index_path(cfg, "gnd", key, self.build, self.files["lds"]["path"], log))

    def build(self, db, _lds, log):
        db.execute("CREATE TABLE records (id TEXT PRIMARY KEY) WITHOUT ROWID")
        db.execute("CREATE TABLE current (old TEXT PRIMARY KEY, cur TEXT) WITHOUT ROWID")
        db.execute("CREATE TABLE deleted (id TEXT PRIMARY KEY) WITHOUT ROWID")
        db.execute("CREATE TABLE links (id TEXT, target TEXT)")
        # the records of the LDS dump and their former numbers
        ids, formers, last, n = [], [], None, 0
        with gzip.open(self.files["lds"]["path"], "rt", encoding="utf-8") as f:
            for line in f:
                n += 1
                m = gen.SUBJECT.match(line)
                if m:
                    k = gen.number(m.group(1))
                    if k != last:
                        ids.append((k,))
                        last = k
                if last and ("deprecatedUri" in line or "owl#sameAs> <https://d-nb.info/gnd/" in line):
                    for x in gen.DEPRECATED.findall(line) + gen.FORMER.findall(line):
                        if gen.number(x) != last:
                            formers.append((gen.number(x), last))
                if len(ids) >= 1_000_000:
                    db.executemany("INSERT OR IGNORE INTO records VALUES (?)", ids)
                    ids = []
                if n % 50_000_000 == 0:
                    log(f"  gnd index: {n:,} lines of the LDS dump")
        db.executemany("INSERT OR IGNORE INTO records VALUES (?)", ids)
        db.executemany("INSERT OR IGNORE INTO current VALUES (?, ?)", formers)
        # the redirect file: redirects (after the former numbers of the records, as generate.py) and deletions
        to, deleted = {}, set()
        with gzip.open(self.files["redirects"]["path"], "rt", encoding="utf-8") as f:
            for o in json.load(f):
                k = gen.gnd_number(o["@id"])
                if not k:
                    continue
                if SAME in o:
                    t = gen.gnd_number(o[SAME][0]["@id"])
                    if t:
                        to[k] = t
                elif gen.DNB + "DeletedResource" in o.get("@type", []):
                    deleted.add(k)
        for k in list(to):
            seen = {k}
            while to[k] in to and to[k] not in seen:
                seen.add(to[k])
                to[k] = to[to[k]]
        db.executemany("INSERT OR IGNORE INTO current VALUES (?, ?)", sorted(to.items()))
        db.executemany("INSERT OR IGNORE INTO deleted VALUES (?)", ((k,) for k in sorted(deleted)))
        log(f"  gnd index: {len(formers):,} former numbers, {len(to):,} redirects, {len(deleted):,} deletions")
        # EntityFacts: the sameAs targets as the dataset writes them
        links, n = [], 0
        with gzip.open(self.files["entityfacts"]["path"], "rt", encoding="utf-8") as f:
            for line in f:
                m = FIRST_ID.search(line)
                if not m:
                    continue
                k = gen.number(m.group(1))
                for x in {x["@id"] for x in json.loads(line).get("sameAs", []) if "@id" in x}:
                    if "[ID]" in x:
                        continue
                    x = gen.BAD_IRI.sub(lambda mm: "%{:02X}".format(ord(mm.group(0))), x.strip().strip('"'))
                    if gen.gnd_number(x) is None and re.match(r"^https?://[^/]+/", x) and not identifiers.is_ours(x):
                        links.append((k, canonical(x)))
                n += 1
                if len(links) >= 1_000_000:
                    db.executemany("INSERT INTO links VALUES (?, ?)", links)
                    links = []
                if n % 1_000_000 == 0:
                    log(f"  gnd index: {n:,} EntityFacts records")
        db.executemany("INSERT INTO links VALUES (?, ?)", links)
        db.execute("CREATE INDEX links_id ON links (id)")

    def seeds(self):
        out = []
        f = resolve(self.cfg, self.cat, gen.INPUTS["freimann"])[0]
        text = open(f["path"], encoding="utf-8").read()
        for k in re.findall(re.escape(gen.JL) + "gnd/(" + gen.NUMBER + ")>", text):
            out.append(("gnd", gen.number(k), "freimann", ""))
        f = resolve(self.cfg, self.cat, gen.INPUTS["ubffm_authors"])[0]
        with open(f["path"], encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                k = gen.gnd_number(r["GND_ID"].strip())
                if k:
                    out.append(("gnd", k, "ubffm-authors", r["PPN_TP_Record"].strip()))
        for f in resolve(self.cfg, self.cat, gen.INPUTS["previous"]):
            opener = gzip.open if f["path"].name.endswith(".gz") else open
            with opener(f["path"], "rt", encoding="utf-8") as fh:
                for line in fh:
                    m = re.match(r"^<" + re.escape(gen.JL) + "gnd/(" + gen.NUMBER + ")>", line)
                    if m:
                        out.append(("gnd", gen.number(m.group(1)), "previous", ""))
        return sorted(set(out)) + static_seeds(self.cfg, self.cat, "gnd")

    def resolve(self, source, ids):
        out = {}
        for i in ids:
            if self.db.execute("SELECT 1 FROM records WHERE id = ?", (i,)).fetchone():
                out[i] = i
                continue
            row = self.db.execute("SELECT cur FROM current WHERE old = ?", (i,)).fetchone()
            if row and self.db.execute("SELECT 1 FROM records WHERE id = ?", (row[0],)).fetchone():
                out[i] = row[0]
            else:
                out[i] = None   # deleted, or in neither the dump nor the redirect file
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
