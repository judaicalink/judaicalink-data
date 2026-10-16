"""Running a generator (decision 0018): generators/<slug>/generate.py -> <build>/<slug>/<run-id>/.

A generator is a Python file with module constants and one function:

    INPUTS = {"crawl": "rujen/2020-09-28/rujen.jsonl.gz"}   # name -> input reference
    PARAMS = {"limit": 0}                                    # defaults; jl generate --param limit=10
    def generate(run): ...

Input references:
    "<slug>/<version>/<path>"   one file of a version (from the store, checked against its checksum)
    "<slug>/<version>"          all RDF data files of a version (without the -meta)
    "<slug>/<run-id>[/<path>]"  output of a run, for development only (add-version refuses it)
    "repo:<path>"               a file of this repository (e.g. catalog/agents.toml), fixed by the commit like
                                the code: uncommitted changes to it are noted, and add-version refuses the run
    "inputs:<source>/<name>[/<path>]"
                                an input that is not published, in the inputs area (decision 0021): all its files, or
                                one; described by its input.toml (origin, description), whose texts the run record copies

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

from . import catalog, corrections, inputs, iris, rdf, runs, turtle
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


def code_state(slug, files=()):
    """(commit, uncommitted paths) of this repository for the generator, the framework and the given files."""
    commit = git("rev-parse", "HEAD")
    status = git("status", "--porcelain", "--", f"generators/{slug}", f":(exclude)generators/{slug}/runs",
                 "src/jl", "jl", *files) or ""
    return commit, [line[3:] for line in status.splitlines()]


_shared = []   # files of other generator folders that the generator being loaded imports (load_shared)


def load_shared(slug, name):
    """A module of another generator's folder, for datasets that share code (0018: they share code, not runs),
    e.g. load_shared("nli-records", "nli_export"). The file is checked for uncommitted changes like the generator's
    own code and named in the run record."""
    path = GENERATORS / slug / f"{name}.py"
    if not path.is_file():
        raise GeneratorError(f"no shared module generators/{slug}/{name}.py")
    spec = importlib.util.spec_from_file_location(f"jl_shared_{slug.replace('-', '_')}_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _shared.append(f"generators/{slug}/{name}.py")
    return module


def load_generator(slug):
    path = GENERATORS / slug / "generate.py"
    _shared.clear()
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
    module._jl_shared = sorted(set(_shared))
    return module


# --- inputs ----------------------------------------------------------------------------------------

def stable_inputs(prefix="", exclude=(), add=None, kinds=None, replaced=False):
    """INPUTS for the stable versions of the catalogue: {prefix + slug (with "_" for "-"): "<slug>/<version>"}.
    exclude: slugs left out; kinds: only these catalogue kinds; replaced: also the datasets that another entry
    replaces (dcterms:replaces); add: {slug: version or run id}, added or instead of the stable version. Evaluated
    when the generator is loaded; the run record names the versions used. slug_of(ref) gives the slug back."""
    cat = catalog.Catalog()
    gone = set() if replaced else {r for e in cat.entries.values() for r in catalog.as_list(e.data.get("replaces"))}
    chosen = {slug: e.stable for slug, e in cat.entries.items()
              if e.stable and slug not in exclude and slug not in gone
              and (kinds is None or e.data.get("kind") in kinds)}
    chosen.update(add or {})
    return {prefix + s.replace("-", "_"): f"{s}/{v}" for s, v in sorted(chosen.items())}


def slug_of(ref):
    """The dataset of an input reference "<slug>/<version>[/<path>]"."""
    return ref.split("/", 1)[0]


def is_meta(name):
    return Path(name).name.split(".")[0].endswith("-meta")


def resolve(cfg, cat, ref):
    """An input reference as a list of {ref, file, sha256, bytes, path (local, not recorded)[, input (texts of an
    input of the inputs area)]}."""
    if isinstance(ref, str) and ref.startswith("repo:"):
        rel = ref[5:]
        p = (ROOT / rel).resolve()
        if ROOT not in p.parents or not p.is_file():
            raise GeneratorError(f"input {ref!r}: no such file in this repository")
        return [{"ref": ref, "file": p.name, "sha256": catalog.sha256(p), "bytes": p.stat().st_size, "path": p}]
    if isinstance(ref, str) and ref.startswith("inputs:"):
        try:
            texts, files = inputs.resolve(cfg.path("inputs"), ref)
        except inputs.InputError as e:
            raise GeneratorError(str(e)) from None
        for f in files:
            f["input"] = texts
        return files
    if not isinstance(ref, str):
        raise GeneratorError(f"input {ref!r}: give a reference string (decision 0021: files made outside are in the "
                             "inputs area, 'inputs:<source>/<name>')")
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
    """What a generator gets: run.input(name), run.inputs(name), run.graph(*names), run.triples(name), run.params,
    run.log(), run.note(), run.write_turtle(path, triples), run.write_deletions(path, blocks), run.copy_input(name),
    run.path(path)."""

    def __init__(self, slug, run_id, directory, params, inputs, logf, deleted=frozenset()):
        self.slug, self.id, self.dir = slug, run_id, directory
        self.params = params
        self._inputs = inputs
        self._logf = logf
        self.notes = []
        self.written = {}   # path -> {triples}
        self.deleted = deleted   # keys of the triples deleted by the stable corrections (decision 0023)
        self.deleted_from = {}   # input name -> number of statements left out

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
        g = Graph()
        n_files = 0
        for n in (names or self._inputs):
            for p in self.inputs(n):
                g.add_file(p, self.deleted)
                n_files += 1
                if g.files[-1]["deleted_by_corrections"]:
                    self.deleted_from[n] = self.deleted_from.get(n, 0) + g.files[-1]["deleted_by_corrections"]
        self.log(f"index: {len(g):,} triples from {n_files} file(s)")
        return g

    def triples(self, name, report=None, file=None):
        """The triples of the RDF files of one input (or of its file named file), as read (no index), without the
        triples deleted by the stable corrections. report: as for rdf.read_triples."""
        for p in self.inputs(name):
            if file is not None and p.name != file:
                continue
            for t in rdf.read_triples(p, report):
                if self.deleted and corrections.key(t) in self.deleted:
                    self.deleted_from[name] = self.deleted_from.get(name, 0) + 1
                    continue
                yield t

    def path(self, rel):
        """A path in the run directory for a file the generator writes itself."""
        p = self.dir / rel
        if p.name in ("run.json", "log.txt") or self.dir not in p.resolve().parents:
            raise GeneratorError(f"not a file name for an output: {rel}")
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def write_turtle(self, rel, triples, prefixes=None):
        check = iris.Check()
        info = turtle.write(self.path(rel), check.watch(triples), prefixes=prefixes)
        self.written[rel] = {"triples": info["triples"]}
        self.log(f"wrote {rel}: {info['triples']:,} triples, {info['bytes']:,} bytes")
        if check.counts:   # IRIs not in canonical form (docs/iri-forms.md)
            self.written[rel]["noncanonical"] = check.summary()
            for k, v in check.summary().items():
                self.log(f"  not canonical ({k}): {v['count']:,}, e.g. {', '.join(v['examples'])}")
        return info

    def write_deletions(self, rel, blocks, prefixes=None):
        """The deletions file of a correction dataset (decision 0023): blocks [(comment lines, triples)]."""
        if not rel.endswith(corrections.SUFFIX):
            raise GeneratorError(f"a deletions file is named <slug>{corrections.SUFFIX}: {rel}")
        info = corrections.write(self.path(rel), blocks, prefixes)
        self.log(f"wrote {rel}: {info['deletions']:,} deletions, {info['bytes']:,} bytes")
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
    shared = getattr(module, "_jl_shared", [])
    commit, dirty = code_state(slug, [r[5:] for r in declared.values() if isinstance(r, str) and r.startswith("repo:")]
                               + shared)
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
    if shared:
        record["shared_code"] = shared
    run = None
    with open(d / "log.txt", "w", encoding="utf-8") as logf:
        try:
            resolved = {name: resolve(cfg, cat, ref) for name, ref in declared.items()}
            record["inputs"] = [{"name": n, **{k: v for k, v in i.items() if k not in ("path", "input")}}
                                for n, files in resolved.items() for i in files]
            described = {i["input"]["input"]: {k: v for k, v in i["input"].items() if k != "input"}
                         for files in resolved.values() for i in files if "input" in i}
            if described:
                record["input_descriptions"] = described
            deleted = set()
            if getattr(module, "CORRECTIONS", True):
                applied = []
                for c_slug, c_version, c_path, _local in corrections.stable_deletions(cat, exclude=(slug,)):
                    f = resolve(cfg, cat, f"{c_slug}/{c_version}/{c_path}")[0]
                    rows = corrections.read(f["path"])
                    deleted.update(corrections.key(t) for t in rows)
                    applied.append({"ref": f["ref"], "sha256": f["sha256"], "deletions": len(rows)})
                if applied:
                    record["corrections"] = applied
            run = Run(slug, run_id, d, params, resolved, logf, frozenset(deleted))
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
            if run.deleted_from:
                record["deleted_by_corrections"] = dict(sorted(run.deleted_from.items()))
        files = []
        for p in sorted(x for x in d.rglob("*") if x.is_file() and x.name not in ("run.json", "log.txt")):
            rel = p.relative_to(d).as_posix()
            f = {"path": rel, "bytes": p.stat().st_size, "sha256": catalog.sha256(p)}
            if run is not None and rel in run.written:
                f["triples"] = run.written[rel]["triples"]
                if "noncanonical" in run.written[rel]:
                    f["noncanonical"] = {k: v["count"] for k, v in run.written[rel]["noncanonical"].items()}
            files.append(f)
        record["files"] = files
    (d / "run.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return d, record
