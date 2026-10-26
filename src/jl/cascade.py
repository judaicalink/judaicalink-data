"""The cascade of the authority datasets as a worklist (decision 0029): which records each authority dataset holds.

The selection starts from the seeds: every identifier of an authority source that our record datasets name (every
statement, jl.identifiers.selects) and our linksets that are not made from the authority datasets (2014links,
interlinks, ls-nli-legacy, a link generator's or manual linksets; not ls-gnd, ls-lc, … which only link what the
authority datasets hold), and the static lists of each authority (Lookup.seeds: manual selections, frozen
selections, the gnd lists). Then, until nothing is pending: each authority resolves its pending identifiers to its
current ones (replacements, redirects; missing ones stay in the selection without a current identifier) and gives
the declared identity links of these records (jl.identifiers.identity); every identifier of another authority source
that is not yet selected becomes pending there; an authority that is searched by other identifiers (Wikidata: items
by GND, VIAF, LC, GeoNames, ISNI number) gets those as search terms. Selections only grow. At the end the selection of
every authority dataset (and what the lookups fetched: the Wikidata answers, the Wikipedia answers) is written to a
directory, which becomes the input of the authority generators (inputs:cascade/<date>).

An authority dataset takes part with a module generators/<slug>/lookup.py that defines

    class Lookup:
        sources = (...)                       # its sources (jl.authorities.SOURCE[slug])
        searched_by = ()                      # other sources it can be searched by (Wikidata)
        def __init__(self, cfg, cat, log): ... # open its inputs and indexes (built once per input, in the cache)
        def seeds(self): -> [(source, identifier, reason, detail)]   # static lists (may be empty)
        def resolve(self, source, ids): -> {id: current id or None}  # None: not in the source (deleted, unknown)
        def links(self, source, ids): -> {id: {(predicate IRI, other source, other id)}}   # of current ids
        def search(self, other_source, ids): -> {other id: {(source, id)}}   # only if searched_by
        def write(self, out, selection): ...  # optional: what the generator needs besides the selection

Identifiers are normalised as jl.identifiers does (identify). The links a Lookup gives are filtered here by the
declaration of its dataset; links to our own records (source judaicalink) are not followed.
"""

import csv
import gzip
import json
import time
from collections import defaultdict
from pathlib import Path

from . import authorities, catalog, corrections, generator, identifiers, rdf


def index_path(cfg, slug, sha256, build, source, log=print):
    """The path of an index of an input (sqlite, in <build>/_index/), built with build(db, source path, log) if it is
    not there yet; named by the checksum of the input, so a new input gets a new index."""
    import sqlite3
    d = cfg.require("build") / "_index"
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{slug}-{sha256[:16]}.sqlite"
    if not path.is_file():
        tmp = path.with_suffix(".building")
        if tmp.exists():
            tmp.unlink()
        log(f"  building the index of {slug} ({source.name}) …")
        db = sqlite3.connect(tmp)
        db.execute("PRAGMA journal_mode = OFF")
        db.execute("PRAGMA synchronous = OFF")
        build(db, source, log)
        db.commit()
        db.close()
        tmp.rename(path)
    return path


def static_seeds(cfg, cat, slug):
    """The static lists of an authority dataset: the inputs its generator names in SEEDS ({reason: input reference}),
    files with the identifier in the first column (and the source in a column "source" where the dataset has
    several); a manual selection or a frozen earlier one. [(source, identifier, reason, detail)]."""
    mod = generator.load_generator(slug)
    out = []
    for reason, ref in getattr(mod, "SEEDS", {}).items():
        for f in generator.resolve(cfg, cat, ref):
            opener = gzip.open if f["path"].name.endswith(".gz") else open
            with opener(f["path"], "rt", encoding="utf-8") as fh:
                rows = list(csv.reader(fh, delimiter="\t"))
            head = rows[0] if rows else []
            si = head.index("source") if "source" in head else None
            ii = 1 if si == 0 else 0
            for r in rows[1:]:
                if r and r[ii].strip():
                    src = r[si] if si is not None else authorities.SOURCE[slug][0]
                    out.append((src, r[ii].strip(), reason, f["file"]))
    return out


def lookups(cfg, cat, log):
    out = {}
    for slug in authorities.SOURCE:
        path = generator.GENERATORS / slug / "lookup.py"
        if path.is_file():
            mod = generator.load_shared(slug, "lookup")
            out[slug] = mod.Lookup(cfg, cat, log)
    return out


def seed_inputs(use):
    """The datasets whose links seed the selection: the stable versions (or use) of all datasets except the authority
    datasets, the linksets made from them, and the datasets without links to records (authorities.NOT_LINKING)."""
    generator.USE.clear()
    generator.USE.update(use)
    try:
        return generator.stable_inputs(exclude=authorities.NOT_LINKING | set(authorities.SOURCE))
    finally:
        generator.USE.clear()


def run(cfg, out, use=None, log=print):
    """Run the cascade; writes <slug>-selection.tsv.gz per authority dataset (and what the lookups write) to out.
    Returns {slug: number of selected identifiers} and the rounds."""
    use = use or {}
    cat = catalog.Catalog()
    t0 = time.time()
    lk = lookups(cfg, cat, log)
    held = {src: slug for slug, l in lk.items() for src in l.sources}
    searched = {src: slug for slug, l in lk.items() for src in getattr(l, "searched_by", ())}
    selected = defaultdict(lambda: defaultdict(set))   # source -> id -> {(reason, detail)}
    current = {}                                       # (source, id) -> current id or None
    pending = defaultdict(set)
    terms = defaultdict(set)                           # searching slug -> {(other source, id)} to search by
    done_terms = set()
    expanded = set()                                   # (source, current id) whose links were followed

    def add(source, ident, reason, detail):
        if source in held:
            if ident not in selected[source]:
                pending[source].add(ident)
            selected[source][ident].add((reason, detail))
        if source in searched:
            t = (source, ident)
            if t not in done_terms:
                terms[searched[source]].add(t)

    # the seeds: our datasets and linksets
    deleted = set()
    for c_slug, c_version, c_path, _local in corrections.stable_deletions(cat):
        f = generator.resolve(cfg, cat, f"{c_slug}/{c_version}/{c_path}")[0]
        deleted.update(corrections.key(t) for t in corrections.read(f["path"]))
    for ref in sorted(seed_inputs(use).values()):
        slug = generator.slug_of(ref)
        n = 0
        for f in generator.resolve(cfg, cat, ref):
            for t in rdf.read_triples(f["path"]):
                if deleted and corrections.key(t) in deleted:
                    continue
                x = identifiers.identify(t[2], t[1])
                if x and (x[0] in held or x[0] in searched):
                    add(x[0], x[1], "linked", slug)
                    n += 1
        log(f"  seeds of {ref}: {n:,} references")
    for slug, l in lk.items():
        for source, ident, reason, detail in l.seeds():
            add(source, identifiers.normal(source, ident), reason, detail)
    log("seeds: " + ", ".join(f"{s} {len(v):,}" for s, v in sorted(selected.items())))

    # the rounds
    rounds = 0
    while any(pending.values()) or any(terms.values()):
        rounds += 1
        work = {s: sorted(v) for s, v in pending.items() if v}
        pending.clear()
        for source, ids in sorted(work.items()):
            slug = held[source]
            cur = lk[slug].resolve(source, ids)
            for i in ids:
                current[(source, i)] = cur.get(i)
                c = cur.get(i)
                if c and c != i and c not in selected[source]:   # the current identifier is selected too
                    selected[source][c].add(("replaces", i))
                    pending[source].add(c)
            live = sorted({c for c in cur.values() if c and (source, c) not in expanded})
            expanded.update((source, c) for c in live)
            for i, ls in lk[slug].links(source, live).items():
                for p, src2, id2 in ls:
                    if src2 != "judaicalink" and identifiers.identity(slug, p, src2):
                        add(src2, identifiers.normal(src2, id2), "linked", slug)
        for slug, ts in sorted((s, t) for s, t in terms.items() if t):
            todo = sorted(ts - done_terms)
            terms[slug] = set()
            done_terms.update(todo)
            by_source = defaultdict(list)
            for src, i in todo:
                by_source[src].append(i)
            for src, ids in sorted(by_source.items()):
                for i, found in lk[slug].search(src, ids).items():
                    for s2, id2 in found:
                        add(s2, id2, f"by-{src}", i)
        log(f"round {rounds}: " + ", ".join(f"{s} {len(v):,}" for s, v in sorted(selected.items()))
            + f"; pending {sum(len(v) for v in pending.values()):,}, search terms {sum(len(v) for v in terms.values()):,}")

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    sizes = {}
    for slug, l in lk.items():
        rows = []
        for source in l.sources:
            for i, reasons in selected[source].items():
                c = current.get((source, i))
                for reason, detail in sorted(reasons):
                    rows.append((source, i, c or "", reason, detail))
        with gzip.open(out / f"{slug}-selection.tsv.gz", "wt", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n")
            w.writerow(["source", "identifier", "current", "reason", "detail"])
            w.writerows(sorted(rows))
        if hasattr(l, "write"):
            l.write(out, {src: dict(selected[src]) for src in l.sources})
        sizes[slug] = sum(len(selected[src]) for src in l.sources)
    (out / "cascade.json").write_text(json.dumps({"rounds": rounds, "seconds": round(time.time() - t0),
                                                  "use": use, "selected": sizes}, indent=1) + "\n")
    return sizes, rounds


CASCADE = "inputs:cascade/2026-10-26/"   # the cascade input the authority generators read (jl cascade, registered)


def selection_input(slug):
    """The input reference of the selection of an authority dataset in the cascade input."""
    return CASCADE + f"{slug}-selection.tsv.gz"


def selection_rows(path):
    """[(source, identifier, current, reason, detail)] of a cascade selection file."""
    with gzip.open(path, "rt", encoding="utf-8") as f:
        r = csv.reader(f, delimiter="\t")
        next(r, None)
        return [tuple(x) for x in r if len(x) == 5]


def read_selection(path):
    """{source: {identifier: current or None}} from a cascade selection file."""
    out = defaultdict(dict)
    with gzip.open(path, "rt", encoding="utf-8") as f:
        r = csv.reader(f, delimiter="\t")
        next(r, None)
        for source, ident, cur, _reason, _detail in r:
            out[source][ident] = cur or None
    return out
