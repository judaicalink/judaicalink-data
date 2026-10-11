"""Running a generator (decision 0018): generators/<slug>/generate.py -> <build>/<slug>/<run-id>/.

A generator is a Python file with module constants and one function:

    INPUTS = {"crawl": "rujen/2020-09-28/rujen.jsonl.gz"}   # name -> input reference
    PARAMS = {"limit": 0}                                    # defaults; jl generate --param limit=10
    def generate(run): ...

Input references:
    "<slug>/<version>/<path>"   one file of a version (from the store, checked against its checksum)
    "<slug>/<version>"          all RDF data files of a version (without the -meta)
    "<slug>/<run-id>[/<path>]"  output of a run, for development only (add-version refuses it)
    {"sha256": ..., "bytes": ..., "origin": "<public URL>"}
                                a file made outside, found by checksum in the store and the `sources` of
                                local.toml; the run record names it by checksum and origin, never by local path

The run object gives the generator its inputs, parameters, a log, the RDF reader and index, and the writers;
everything it writes goes into the run directory. The run record (run.json) names the generator, the commit
of this repository and whether the code had uncommitted changes, Python, parameters, inputs (by reference and
checksum) and the files written (size, checksum, triples), and notes; never local paths.
"""

import datetime
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

from . import catalog, rdf, runs, turtle
from .config import GENERATORS, ROOT
from .graph import Graph


class GeneratorError(Exception):
    pass


def git(*args):
    try:
        out = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, timeout=30)
    except OSError:
        return None
    return out.stdout.rstrip("\n") if out.returncode == 0 else None


def code_state(slug):
    """(commit, uncommitted paths) of this repository for the generator and the framework."""
    commit = git("rev-parse", "HEAD")
    status = git("status", "--porcelain", "--", f"generators/{slug}", "src/jl", "jl") or ""
    return commit, [line[3:] for line in status.splitlines()]


def load_generator(slug):
    path = GENERATORS / slug / "generate.py"
    if not path.is_file():
        raise GeneratorError(f"no generator: generators/{slug}/generate.py")
    spec = importlib.util.spec_from_file_location(f"jl_generator_{slug.replace('-', '_')}", path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))   # helper modules next to generate.py
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
    if not callable(getattr(module, "generate", None)):
        raise GeneratorError(f"generators/{slug}/generate.py has no function generate(run)")
    return module


# --- inputs ----------------------------------------------------------------------------------------

def is_meta(name):
    return Path(name).name.split(".")[0].endswith("-meta")


def find_by_checksum(sha, size, dirs):
    for d in dirs:
        if not d.is_dir():
            continue
        for p in d.rglob("*"):
            if p.is_file() and not p.is_symlink() and (size is None or p.stat().st_size == size):
                if catalog.sha256(p) == sha:
                    return p
    return None


def resolve(cfg, cat, ref):
    """An input reference as a list of {ref, file, sha256, bytes, path (local, not recorded)}."""
    if isinstance(ref, dict):
        sha, size = ref.get("sha256"), ref.get("bytes")
        if not sha or not ref.get("origin"):
            raise GeneratorError(f"an outside input needs sha256 and origin: {ref}")
        dirs = [d for d in [cfg.store] if d] + cfg.paths("sources")
        p = find_by_checksum(sha, size, dirs)
        if p is None:
            raise GeneratorError(f"input {sha[:12]}… ({ref['origin']}) not found in the store or the sources "
                                 "of local.toml")
        return [{"ref": {"origin": ref["origin"]}, "file": p.name, "sha256": sha, "bytes": p.stat().st_size,
                 "path": p}]
    slug, _, rest = ref.partition("/")
    head, _, path = rest.partition("/")
    if not head:
        raise GeneratorError(f"input {ref!r}: give <slug>/<version>[/<path>] or <slug>/<run-id>[/<path>]")
    if runs.is_run_id(head):
        r = runs.get_run(cfg.require("build"), slug, head)
        if r is None:
            raise GeneratorError(f"input {ref!r}: no such run")
        files = {f["path"]: f.get("sha256") for f in (r["record"] or {}).get("files", [])}
        base = r["dir"]
    else:
        e = cat.get(slug)
        v = e.version(head) if e else None
        if v is None:
            raise GeneratorError(f"input {ref!r}: no such version in the catalogue")
        files = {f["path"]: f.get("sha256") for f in v.get("files", []) if isinstance(f, dict)}
        rec = runs.version_record(slug, head) or {}
        for f in rec.get("files", []):   # files of the version kept only in the store
            files.setdefault(f.get("path"), f.get("sha256"))
        base = cfg.require("store") / slug / head
    if path:
        if path not in files:
            raise GeneratorError(f"input {ref!r}: {path} is not a file of {slug}/{head}")
        chosen = [path]
    else:
        chosen = [p for p in files if rdf.rdf_format(p) and not is_meta(p)]
        if not chosen:
            raise GeneratorError(f"input {ref!r}: no RDF data files")
    out = []
    for p in chosen:
        local = base / p
        if not local.is_file():
            raise GeneratorError(f"input {slug}/{head}/{p} is not in {base.parent.parent}")
        sha = catalog.sha256(local)
        if files[p] and sha != files[p]:
            raise GeneratorError(f"input {slug}/{head}/{p}: checksum differs from the catalogue or run record")
        out.append({"ref": f"{slug}/{head}/{p}", "file": Path(p).name, "sha256": sha,
                    "bytes": local.stat().st_size, "path": local})
    return out


# --- the run ---------------------------------------------------------------------------------------

def utc(t=None):
    return datetime.datetime.fromtimestamp(t or time.time(), datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Run:
    """What a generator gets: run.input(name), run.inputs(name), run.graph(*names), run.params, run.log(),
    run.note(), run.write_turtle(path, triples), run.copy_input(name), run.path(path)."""

    def __init__(self, slug, run_id, directory, params, inputs, logf):
        self.slug, self.id, self.dir = slug, run_id, directory
        self.params = params
        self._inputs = inputs
        self._logf = logf
        self.notes = []
        self.written = {}   # path -> {triples}

    def log(self, *msg):
        line = " ".join(str(m) for m in msg)
        self._logf.write(line + "\n")
        self._logf.flush()

    def note(self, text):
        """A remark for the run record (e.g. a hand step, a known deviation)."""
        self.notes.append(text)
        self.log("note:", text)

    def inputs(self, name):
        if name not in self._inputs:
            raise GeneratorError(f"undeclared input {name!r} (INPUTS: {', '.join(self._inputs)})")
        return [i["path"] for i in self._inputs[name]]

    def input(self, name):
        paths = self.inputs(name)
        if len(paths) != 1:
            raise GeneratorError(f"input {name!r} has {len(paths)} files; use run.inputs()")
        return paths[0]

    def graph(self, *names):
        """The framework's index of the RDF files of the named inputs (all inputs if none are named)."""
        paths = [p for n in (names or self._inputs) for p in self.inputs(n)]
        g = Graph.load(paths)
        self.log(f"index: {len(g):,} triples from {len(paths)} file(s)")
        return g

    def triples(self, name):
        """The triples of the RDF files of one input, as read (no index)."""
        for p in self.inputs(name):
            yield from rdf.read_triples(p)

    def path(self, rel):
        """A path in the run directory for a file the generator writes itself."""
        p = self.dir / rel
        if p.name in ("run.json", "log.txt") or self.dir not in p.resolve().parents:
            raise GeneratorError(f"not a file name for an output: {rel}")
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def write_turtle(self, rel, triples, prefixes=None):
        info = turtle.write(self.path(rel), triples, prefixes=prefixes)
        self.written[rel] = {"triples": info["triples"]}
        self.log(f"wrote {rel}: {info['triples']:,} triples, {info['bytes']:,} bytes")
        return info

    def copy_input(self, name, rel=None):
        """Copy an input file into the run (e.g. a crawl that is published with the version)."""
        src = self.input(name)
        dst = self.path(rel or src.name)
        shutil.copyfile(src, dst)
        self.log(f"copied input {name} to {dst.relative_to(self.dir)}")
        return dst


def parse_params(defaults, given):
    params = dict(defaults)
    for item in given:
        k, sep, v = item.partition("=")
        if not sep or k not in defaults:
            raise GeneratorError(f"unknown parameter {k!r} (PARAMS: {', '.join(defaults) or 'none'})")
        d = defaults[k]
        params[k] = (v.lower() in ("1", "true", "yes") if isinstance(d, bool) else type(d)(v)
                     if isinstance(d, (int, float)) and not isinstance(d, bool) else v)
    return params


def generate(cfg, slug, given_params=(), input_overrides=(), log=print):
    """Run the generator of a dataset; returns the run directory. The run record is written also when the
    generator fails (status "failed")."""
    cat = catalog.Catalog()
    if cat.get(slug) is None:
        raise GeneratorError(f"no dataset {slug!r} in the catalogue")
    module = load_generator(slug)
    declared = dict(getattr(module, "INPUTS", {}))
    for item in input_overrides:
        k, sep, v = item.partition("=")
        if not sep or k not in declared:
            raise GeneratorError(f"unknown input {k!r} (INPUTS: {', '.join(declared) or 'none'})")
        declared[k] = v
    params = parse_params(getattr(module, "PARAMS", {}), given_params)
    commit, dirty = code_state(slug)
    started = time.time()
    run_id = "run-" + datetime.datetime.fromtimestamp(started, datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = cfg.require("build") / slug / run_id
    while d.exists():   # two runs in the same second
        time.sleep(1)
        started = time.time()
        run_id = "run-" + datetime.datetime.fromtimestamp(started, datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        d = cfg.require("build") / slug / run_id
    d.mkdir(parents=True)
    record = {"slug": slug, "run": run_id, "generator": f"generators/{slug}/generate.py", "commit": commit,
              "uncommitted": dirty, "python": platform.python_version(), "params": params,
              "input_overrides": list(input_overrides), "started": utc(started)}
    run = None
    with open(d / "log.txt", "w", encoding="utf-8") as logf:
        try:
            inputs = {name: resolve(cfg, cat, ref) for name, ref in declared.items()}
            record["inputs"] = [{"name": n, **{k: v for k, v in i.items() if k != "path"}}
                                for n, files in inputs.items() for i in files]
            run = Run(slug, run_id, d, params, inputs, logf)
            run.log(f"{slug}/{run_id}: commit {commit}" + (f" (uncommitted: {', '.join(dirty)})" if dirty else ""))
            module.generate(run)
            record["status"] = "ok"
        except Exception as e:
            record["status"] = "failed"
            record["error"] = f"{type(e).__name__}: {e}"
            logf.write(traceback.format_exc())
        record["finished"] = utc()
        record["seconds"] = round(time.time() - started, 1)
        if run is not None:
            record["notes"] = run.notes
        files = []
        for p in sorted(x for x in d.rglob("*") if x.is_file() and x.name not in ("run.json", "log.txt")):
            rel = p.relative_to(d).as_posix()
            f = {"path": rel, "bytes": p.stat().st_size, "sha256": catalog.sha256(p)}
            if run is not None and rel in run.written:
                f["triples"] = run.written[rel]["triples"]
            files.append(f)
        record["files"] = files
    (d / "run.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return d, record
