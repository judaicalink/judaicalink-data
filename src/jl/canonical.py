"""The canonical form of RDF files and comparisons on it (decision 0018).

The canonical form of a file is its triples as N-Triples lines, sorted by code point (the order of
`LC_ALL=C sort`) and deduplicated, with only the normalisation that RDF 1.1 term equality allows: no
xsd:string datatype, lower-case language tags. Escapes are those of canonical N-Triples. The canonical form
of several files is the union of theirs.

Canonical forms are cached per file checksum in the cache directory (local.toml `cache`, default
<build>/.cache), canonical/<sha256>.nt.gz with <sha256>.json (counts, what the reader met).
"""

import gzip
import hashlib
import heapq
import json
import os
import tempfile
from pathlib import Path

from . import catalog, rdf

# Bump when the reader or the canonical form changes; cached forms of another version are rebuilt.
CANONICAL_VERSION = 2
CHUNK_LINES = 2_000_000


def cache_dir(cfg):
    d = cfg.path("cache") or (cfg.require("build") / ".cache")
    return d / "canonical"


def _dedup(lines):
    last = None
    for line in lines:
        if line != last:
            yield line
            last = line


def _sorted_unique(lines, tmpdir):
    """Sort and deduplicate a stream of lines; external merge sort in chunks of CHUNK_LINES."""
    chunks, buf = [], []
    for line in lines:
        buf.append(line)
        if len(buf) >= CHUNK_LINES:
            buf.sort()
            fd, name = tempfile.mkstemp(dir=tmpdir, suffix=".nt")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                for x in _dedup(buf):
                    f.write(x + "\n")
            chunks.append(name)
            buf = []
    buf.sort()
    if not chunks:
        yield from _dedup(buf)
        return
    files = [open(c, encoding="utf-8") for c in chunks]
    try:
        streams = [(x.rstrip("\n") for x in f) for f in files] + [iter(buf)]
        yield from _dedup(heapq.merge(*streams))
    finally:
        for f, c in zip(files, chunks):
            f.close()
            os.unlink(c)


def canonical(path, cfg, sha=None):
    """Make (or find in the cache) the canonical form of one file. Returns its info dict:
    sha256, triples (distinct), statements (as read, with duplicates), blank_node_triples, rdf_star, members,
    and 'canonical' (the cached .nt.gz)."""
    path = Path(path)
    sha = sha or catalog.sha256(path)
    d = cache_dir(cfg)
    info_path, nt_path = d / f"{sha}.json", d / f"{sha}.nt.gz"
    if info_path.is_file() and nt_path.is_file():
        info = json.loads(info_path.read_text(encoding="utf-8"))
        if info.get("canonical_version") == CANONICAL_VERSION:
            info["canonical"] = str(nt_path)
            return info
    d.mkdir(parents=True, exist_ok=True)
    report = {}
    counts = {"statements": 0, "blank_node_triples": 0}

    def lines():
        for s, p, o in rdf.read_triples(path, report):
            counts["statements"] += 1
            if isinstance(s, rdf.BNode) or isinstance(o, rdf.BNode):
                counts["blank_node_triples"] += 1
            yield rdf.nt_line(s, p, o, canonical=True)

    n = 0
    tmp = nt_path.with_suffix(".tmp")
    with tempfile.TemporaryDirectory(dir=d) as tmpdir:
        with gzip.open(tmp, "wt", encoding="utf-8", compresslevel=1) as f:
            for line in _sorted_unique(lines(), tmpdir):
                f.write(line + "\n")
                n += 1
    os.replace(tmp, nt_path)
    info = {"canonical_version": CANONICAL_VERSION, "sha256": sha, "name": path.name, "triples": n,
            "statements": counts["statements"], "blank_node_triples": counts["blank_node_triples"],
            "rdf_star": report.get("rdf_star", 0), "members": [Path(m).name for m in report.get("members", [])]}
    info_path.write_text(json.dumps(info, indent=1) + "\n", encoding="utf-8")
    info["canonical"] = str(nt_path)
    return info


def cached_info(sha, cfg):
    """The cached info of a file checksum, or None (no reading of the file)."""
    d = cache_dir(cfg)
    try:
        info = json.loads((d / f"{sha}.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if info.get("canonical_version") != CANONICAL_VERSION or not (d / f"{sha}.nt.gz").is_file():
        return None
    info["canonical"] = str(d / f"{sha}.nt.gz")
    return info


def lines(info):
    with gzip.open(info["canonical"], "rt", encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n")


def union(infos):
    """The canonical lines of several files (sorted, deduplicated)."""
    if len(infos) == 1:
        yield from lines(infos[0])
        return
    yield from _dedup(heapq.merge(*(lines(i) for i in infos)))


def union_count(infos, cfg, make=False):
    """Distinct triples in the union of several files, cached by their checksums; None if not cached and
    make is False."""
    shas = sorted(i["sha256"] for i in infos)
    key = hashlib.sha256(" ".join(shas).encode()).hexdigest()[:20]
    p = cache_dir(cfg) / f"union-{key}.json"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if data.get("canonical_version") == CANONICAL_VERSION and data.get("files") == shas:
            return data["triples"]
    except (OSError, ValueError):
        pass
    if not make:
        return None
    n = sum(1 for _ in union(infos))
    p.write_text(json.dumps({"canonical_version": CANONICAL_VERSION, "files": shas, "triples": n}, indent=1)
                 + "\n", encoding="utf-8")
    return n


def compare(a, b, examples=5, write=None):
    """Compare two sorted, deduplicated line streams. Returns counts and the first examples of each side;
    write: optional (file for lines only in a, file for lines only in b)."""
    res = {"a": 0, "b": 0, "common": 0, "only_a": 0, "only_b": 0, "examples_only_a": [], "examples_only_b": []}
    sentinel = None
    ia, ib = iter(a), iter(b)
    x, y = next(ia, sentinel), next(ib, sentinel)

    def only(side, line):
        res["only_" + side] += 1
        if len(res["examples_only_" + side]) < examples:
            res["examples_only_" + side].append(line)
        if write:
            write[0 if side == "a" else 1].write(line + "\n")

    while x is not sentinel or y is not sentinel:
        if y is sentinel or (x is not sentinel and x < y):
            res["a"] += 1
            only("a", x)
            x = next(ia, sentinel)
        elif x is sentinel or y < x:
            res["b"] += 1
            only("b", y)
            y = next(ib, sentinel)
        else:
            res["a"] += 1
            res["b"] += 1
            res["common"] += 1
            x, y = next(ia, sentinel), next(ib, sentinel)
    res["identical"] = res["only_a"] == 0 and res["only_b"] == 0
    return res
