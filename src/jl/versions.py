"""From a run to a version, and rendering the -meta of a version (decision 0018).

add-version <slug>/<run-id>: refuses runs that failed, ran uncommitted code or used runs as inputs; gives the
version id (default the run date, "-2", "-3" … if taken); writes the header comments into the Turtle files
the generator wrote; renders the -meta; copies the run record to generators/<slug>/runs/<version>.json (with
the files as they are in the version); adds the version and a changelog entry to the catalogue entry; moves
the files into the store <slug>/<version>/. It does not move `stable` and publishes nothing.

render-meta <slug>/<version>: renders the -meta again and replaces it (and its size and checksum in the
entry) only when its content changed (0018).

The catalogue entry is edited as text (comments and layout stay); every edit is checked by parsing the result
and comparing it with the expected data.
"""

import copy
import datetime
import json
import os
import re
import shutil
import subprocess
import tomllib

from . import canonical, catalog, generator, meta, rdf, runs, turtle
from .agents import Registry
from .config import ROOT


class VersionError(LookupError):
    pass


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def framework_state():
    """(commit, uncommitted framework paths)."""
    commit = generator.git("rev-parse", "HEAD")
    status = generator.git("status", "--porcelain", "--", "src/jl", "jl") or ""
    return commit, [line[3:] for line in status.splitlines()]


def git_user():
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "config", "user.name"], capture_output=True, text=True)
    except OSError:
        return None
    return out.stdout.strip() or None


# --- editing an entry as text ----------------------------------------------------------------------

def toml_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, list):
        return "[" + ", ".join(toml_value(x) for x in v) + "]"
    return json.dumps(str(v), ensure_ascii=False)


FILE_KEYS = ("path", "description", "bytes", "sha256", "triples")


def files_block(f, indent="  "):
    lines = [f"{indent}[[versions.files]]"]
    lines += [f"{indent}{k} = {toml_value(f[k])}" for k in FILE_KEYS if f.get(k) is not None]
    return lines


def version_block(v):
    lines = ["[[versions]]"]
    lines += [f"{k} = {toml_value(v[k])}" for k in ("version", "issued", "author", "commit", "graph",
                                                   "description", "withdrawn") if v.get(k) is not None]
    for f in v.get("files", []):
        lines += [""] + files_block(f)
    return lines


def changelog_block(c):
    return ["[[changelog]]"] + [f"{k} = {toml_value(c[k])}" for k in ("date", "version", "author", "text", "refs")
                                if c.get(k) is not None]


def split_entry(text):
    m = catalog.FRONT_MATTER.match(text)
    if not m:
        raise VersionError("entry without TOML front matter")
    return text[:m.start(1)], m.group(1), text[m.end(1):]


def insert_before(lines, patterns, block):
    """Insert block (and an empty line) before the first line matching one of the patterns, in order of the
    patterns; at the end if none matches."""
    for pat in patterns:
        for i, line in enumerate(lines):
            if re.match(pat, line):
                return lines[:i] + block + [""] + lines[i:]
    while lines and not lines[-1].strip():
        lines = lines[:-1]
    return lines + [""] + block


def checked(text, expected):
    _, fm, _ = split_entry(text)
    data = tomllib.loads(fm)
    if data != expected:
        raise VersionError("internal error: the edited entry does not parse to the expected data; nothing written")
    return text


def add_version_text(text, data, version, change):
    """The entry text with a new version (newest first) and a changelog entry (newest first)."""
    head, fm, tail = split_entry(text)
    lines = fm.split("\n")
    lines = insert_before(lines, [r"^\[\[versions\]\]", r"^\[\[changelog\]\]"], version_block(version))
    lines = insert_before(lines, [r"^\[\[changelog\]\]"], changelog_block(change))
    expected = copy.deepcopy(data)
    expected["versions"] = [version] + list(data.get("versions", []))
    expected["changelog"] = [change] + list(data.get("changelog", []))
    return checked(head + "\n".join(lines) + tail, expected)


def set_file_text(text, data, vid, f):
    """The entry text with the file f (by path) of version vid set to the given values (added if missing)."""
    head, fm, tail = split_entry(text)
    lines = fm.split("\n")
    headers = [i for i, line in enumerate(lines) if re.match(r"^\s*\[", line)]

    def key(i, name):
        """The value of name in the table starting at line i, as TOML text."""
        j = i + 1
        while j < len(lines) and j not in headers:
            m = re.match(rf"^\s*{name}\s*=\s*(.*?)\s*$", lines[j])
            if m:
                return m.group(1)
            j += 1
        return None

    def end_of(i, inner):
        """The line after the table at i and the tables following it whose header matches inner."""
        for h in headers:
            if h > i and not re.match(inner, lines[h]):
                return h
        return len(lines)

    vstart = next((h for h in headers if re.match(r"^\s*\[\[versions\]\]", lines[h])
                   and key(h, "version") == toml_value(vid)), None)
    if vstart is None:
        raise VersionError(f"version {vid} not found in the entry")
    vend = end_of(vstart, r"^\s*\[\[versions\.files\]\]")
    fstart = next((h for h in headers if vstart < h < vend and key(h, "path") == toml_value(f["path"])), None)
    values = {k: v for k, v in f.items() if v is not None}
    if fstart is not None:
        fend = next((h for h in headers if h > fstart), len(lines))
        fend = min(fend, vend)
        while fend > fstart and not lines[fend - 1].strip():
            fend -= 1
        indent = re.match(r"^(\s*)", lines[fstart]).group(1)
        old = tomllib.loads("\n".join(x.strip() for x in lines[fstart + 1:fend]))
        lines = lines[:fstart] + files_block({**old, **values}, indent) + lines[fend:]
    else:
        trail = vend
        while trail > vstart and not lines[trail - 1].strip():
            trail -= 1
        lines = lines[:trail] + [""] + files_block(values) + lines[trail:]
    expected = copy.deepcopy(data)
    for v in expected.get("versions", []):
        if v.get("version") == vid:
            files = v.setdefault("files", [])
            for x in files:
                if x.get("path") == f["path"]:
                    x.update(values)
                    break
            else:
                files.append(values)
    return checked(head + "\n".join(lines) + tail, expected)


# --- measuring and rendering -----------------------------------------------------------------------

def rdf_data(path):
    return rdf.rdf_format(path) is not None and not generator.is_meta(path)


def measure(cfg, files, base):
    """Fill in triples of RDF files and return the statistics of the RDF data files (None if there are none)."""
    infos = []
    for f in files:
        if rdf.rdf_format(f["path"]) is None:
            continue
        info = canonical.canonical(base / f["path"], cfg, f.get("sha256"))
        if f.get("triples") is None:
            f["triples"] = info["triples"]
        if rdf_data(f["path"]):
            infos.append(info)
    return meta.statistics(infos) if infos else None


def write_meta(path, entry, version, public, record, stats, registry, commit):
    """Render and write the -meta; returns its file info."""
    slug, vid = entry.name, version["version"]
    triples = meta.render(entry, version, public, record, stats, registry)
    triples += meta.provenance(slug, vid, commit, now_utc())
    info = turtle.write(path, triples, header=meta.header(slug, vid, meta=True))
    return {"path": meta.meta_path(slug), "bytes": info["bytes"], "sha256": info["sha256"], "triples": info["triples"]}


# --- add-version -----------------------------------------------------------------------------------

def default_version(cat_entry, store_dir, slug, run):
    base = run["id"][4:8] + "-" + run["id"][8:10] + "-" + run["id"][10:12]
    taken = {v.get("version") for v in cat_entry.versions()}
    vid, n = base, 1
    while vid in taken or (store_dir / slug / vid).exists() or runs.record_path(slug, vid).exists():
        n += 1
        vid = f"{base}-{n}"
    return vid


def add_version(cfg, slug, run_id, version=None, author=None, store_only=(), description=None, text=None,
                issued=None, dry_run=False, log=print):
    """Make a run a version. Returns (version id, directory, the version table, warnings)."""
    cat = catalog.Catalog()
    e = cat.get(slug)
    if e is None:
        raise VersionError(f"no dataset '{slug}' in the catalogue")
    store = cfg.require("store")
    run = runs.get_run(cfg.require("build"), slug, run_id)
    if run is None or not run["record"]:
        raise VersionError(f"no run {slug}/{run_id} with a run record")
    rec = run["record"]
    if rec.get("status") != "ok":
        raise VersionError(f"{slug}/{run_id} did not finish (status {rec.get('status')})")
    if rec.get("uncommitted"):
        raise VersionError(f"{slug}/{run_id} ran uncommitted code or files: {', '.join(rec['uncommitted'])}")
    if not rec.get("commit"):
        raise VersionError(f"{slug}/{run_id} has no commit")
    for i in rec.get("inputs", []):
        ref = i.get("ref")
        if isinstance(ref, str) and not ref.startswith("repo:") and runs.is_run_id(ref.split("/")[1]):
            raise VersionError(f"input {i.get('name')} is a run ({ref}); make it a version first")
    became = runs.version_of_run(slug, run_id)
    if became:
        raise VersionError(f"{slug}/{run_id} is already the version {became}")
    commit, dirty = framework_state()
    if dirty and not dry_run:
        raise VersionError(f"the framework has uncommitted changes ({', '.join(dirty)}); the -meta names its commit")

    registry = Registry()
    author = author or git_user()
    if not author:
        raise VersionError("no author (--author, or git config user.name)")
    registry.number(author)
    vid = version or default_version(e, store, slug, run)
    if not catalog.SLUG.match(vid) or vid in catalog.RESERVED_VERSIONS:
        raise VersionError(f"'{vid}' is not a valid version id")
    if e.version(vid) or (store / slug / vid).exists() or runs.record_path(slug, vid).exists():
        raise VersionError(f"version {slug}/{vid} exists already")

    warnings = []
    for i in rec.get("inputs", []):
        ref = i.get("ref")
        if isinstance(ref, dict) and not meta.is_url(ref.get("origin")):
            warnings.append(f"input {i.get('name')} ({i.get('file')}, sha256 {i.get('sha256', '')[:12]}…) has no URL "
                            f"as origin ({ref.get('origin')!r}): decide whether to keep it with this version (0018, 0019)")

    # the files of the run, checked against the run record
    files = [dict(f) for f in rec.get("files", [])]
    names = {f["path"] for f in files}
    for p in store_only:
        if p not in names:
            raise VersionError(f"--store-only {p}: not a file of the run")
    if meta.meta_path(slug) in names:
        raise VersionError(f"the run wrote {meta.meta_path(slug)}; the -meta is rendered by the framework")
    for f in files:
        local = run["dir"] / f["path"]
        if not local.is_file() or catalog.sha256(local) != f["sha256"]:
            raise VersionError(f"{f['path']} in the run directory differs from the run record")

    target = store / slug / vid
    if dry_run:
        target = cfg.require("build") / slug / f"{run_id}-as-{vid}"
        if target.exists():
            shutil.rmtree(target)
    stage = target.with_name(f".{target.name}.tmp")
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    try:
        for f in files:
            dst = stage / f["path"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(run["dir"] / f["path"], dst)
            if rec.get("mode") != "import" and "triples" in f and rdf.rdf_format(f["path"]) == "turtle":
                # written by the generator (imported files and copied inputs keep their bytes)
                f.update(turtle.add_header(dst, meta.header(slug, vid)))
        stats = measure(cfg, files, stage)
        public = [{k: f.get(k) for k in ("path", "bytes", "sha256", "triples")} for f in files
                  if f["path"] not in store_only]
        if issued and not catalog.is_date(issued):
            raise VersionError(f"--issued {issued}: not a date")
        vtable = {"version": vid, "issued": issued or rec["started"][:10], "author": author, "commit": rec["commit"]}
        if description:
            vtable["description"] = description
        m = write_meta(stage / meta.meta_path(slug), e, vtable, public, rec, stats, registry, commit)
        vtable["files"] = [{k: v for k, v in f.items() if v is not None} for f in public] + [m]
        change = {"date": datetime.date.today().isoformat(), "version": vid, "author": author,
                  "text": text or (f"New version, imported ({run_id})." if rec.get("mode") == "import" else
                                   f"New version, made by the generator in judaicalink-data ({run_id}).")}
        entry_text = add_version_text(e.path.read_text(encoding="utf-8"), e.data, vtable, change)
        record = dict(rec)
        record["version"] = vid
        record["files"] = files
        record_text = json.dumps(record, indent=1, ensure_ascii=False) + "\n"
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise

    if dry_run:
        os.replace(stage, target)
        (target / "run.json").write_text(record_text, encoding="utf-8")
        (target / "catalog-entry.md").write_text(entry_text, encoding="utf-8")
        return vid, target, vtable, warnings
    os.replace(stage, target)
    rp = runs.record_path(slug, vid)
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(record_text, encoding="utf-8")
    e.path.write_text(entry_text, encoding="utf-8")
    for f in files:   # moved: the run keeps its record and log
        (run["dir"] / f["path"]).unlink()
    return vid, target, vtable, warnings


# --- render-meta -----------------------------------------------------------------------------------

def render_meta(cfg, slug, vid, dry_run=False, out=None):
    """Render the -meta of a version again. Returns (status, info): 'unchanged', 'written' or 'would write'.
    With out, the -meta is written to that file instead (nothing else changes)."""
    cat = catalog.Catalog()
    e = cat.get(slug)
    v = e.version(vid) if e else None
    if v is None:
        raise VersionError(f"no version {slug}/{vid} in the catalogue")
    commit, dirty = framework_state()
    if dirty and not (dry_run or out):
        raise VersionError(f"the framework has uncommitted changes ({', '.join(dirty)}); the -meta names its commit")
    base = cfg.require("store") / slug / vid
    mp = meta.meta_path(slug)
    public = [{k: f.get(k) for k in ("path", "bytes", "sha256", "triples", "description")}
              for f in v.get("files", []) if isinstance(f, dict) and f.get("path") != mp]
    for f in public:
        if not (base / f["path"]).is_file():
            raise VersionError(f"{slug}/{vid}/{f['path']} is not in the store")
    stats = measure(cfg, public, base)
    rec = runs.version_record(slug, vid)
    registry = Registry()
    content = meta.content_lines(meta.render(e, v, public, rec, stats, registry), slug, vid)
    existing = base / mp
    if out is None and existing.is_file() and meta.read_content(existing, slug, vid) == content:
        return "unchanged", None
    if out is not None:
        return "written", write_meta(out, e, v, public, rec, stats, registry, commit)
    if dry_run:
        return "would write", None
    tmp = base / f".tmp-{mp}"
    info = write_meta(tmp, e, v, public, rec, stats, registry, commit)
    entry_text = set_file_text(e.path.read_text(encoding="utf-8"), e.data, vid,
                               {k: info[k] for k in ("path", "bytes", "sha256", "triples")})
    os.replace(tmp, existing)
    e.path.write_text(entry_text, encoding="utf-8")
    return "written", info


def render_meta_all(cfg, dry_run=False, log=print):
    """render-meta for every version of the catalogue that has files. Returns {status: count}."""
    counts = {}
    for slug, e in sorted(catalog.Catalog().entries.items()):
        for v in e.versions():
            if not any(isinstance(f, dict) and f.get("path") != meta.meta_path(slug) for f in v.get("files", [])):
                continue
            status, info = render_meta(cfg, slug, v["version"], dry_run=dry_run)
            counts[status] = counts.get(status, 0) + 1
            log(f"{slug}/{v['version']}: {status}" + (f" ({info['triples']} triples)" if info else ""))
    return counts


# --- import-files ----------------------------------------------------------------------------------

def import_version(cfg, slug, vid, description, origin=None, sources=(), notes=(), dry_run=False):
    """Attach a run record (mode "import") to a catalogued version made outside the framework. No file of the
    version changes; the record says what is known about how it was made. Returns the record."""
    e = catalog.Catalog().get(slug)
    v = e.version(vid) if e else None
    if v is None:
        raise VersionError(f"no version {slug}/{vid} in the catalogue")
    if runs.record_path(slug, vid).exists():
        raise VersionError(f"{slug}/{vid} has a run record already")
    if not description:
        raise VersionError("--description is required")
    commit, dirty = generator.code_state(slug)
    if dirty and not dry_run:
        raise VersionError(f"uncommitted changes ({', '.join(dirty)}); the record names the commit")
    base = cfg.require("store") / slug / vid
    files = []
    for f in v.get("files", []):
        if not isinstance(f, dict) or f.get("path") == meta.meta_path(slug):
            continue
        local = base / f["path"]
        if not local.is_file():
            raise VersionError(f"{slug}/{vid}/{f['path']} is not in the store")
        sha = catalog.sha256(local)
        if f.get("sha256") and sha != f["sha256"]:
            raise VersionError(f"{slug}/{vid}/{f['path']}: checksum differs from the catalogue")
        files.append({"path": f["path"], "bytes": local.stat().st_size, "sha256": sha})
    measure(cfg, files, base)
    record = {"slug": slug, "version": vid, "mode": "import", "imported": now_utc(), "commit": commit,
              "description": description}
    if origin:
        record["origin"] = origin
    record["sources"] = list(sources)
    record["notes"] = list(notes)
    record["files"] = files
    if not dry_run:
        p = runs.record_path(slug, vid)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return record


def import_files(cfg, slug, paths, origin, description, sources=(), notes=()):
    """Take files made elsewhere in as a run (mode "import"); add-version makes it a version. The files are
    kept byte for byte (no header comments). Files with blank nodes are refused (0018). Returns (dir, record)."""
    if catalog.Catalog().get(slug) is None:
        raise VersionError(f"no dataset '{slug}' in the catalogue")
    if not origin or not description:
        raise VersionError("--origin and --description are required: where the files come from and what they are")
    srcs = []
    for p in paths:
        p = p.expanduser().resolve()
        if not p.is_file():
            raise VersionError(f"{p}: not a file")
        srcs.append(p)
    names = [p.name for p in srcs]
    if len(set(names)) != len(names):
        raise VersionError("two files with the same name")
    if meta.meta_path(slug) in names:
        raise VersionError(f"{meta.meta_path(slug)} is rendered by the framework, not imported")
    for p in srcs:
        if rdf.rdf_format(p.name):
            info = canonical.canonical(p, cfg)
            if info["blank_node_triples"]:
                raise VersionError(f"{p.name}: {info['blank_node_triples']:,} triples with blank nodes; blank nodes "
                                   "are not taken in (0018)")
    commit, dirty = framework_state()
    started = datetime.datetime.now(datetime.timezone.utc)
    run_id = "run-" + started.strftime("%Y%m%dT%H%M%SZ")
    d = cfg.require("build") / slug / run_id
    if d.exists():
        raise VersionError(f"{d} exists; try again in a second")
    d.mkdir(parents=True)
    files = []
    for p in srcs:
        shutil.copyfile(p, d / p.name)
        files.append({"path": p.name, "bytes": p.stat().st_size, "sha256": catalog.sha256(d / p.name)})
    record = {"slug": slug, "run": run_id, "mode": "import", "commit": commit, "uncommitted": dirty,
              "started": started.strftime("%Y-%m-%dT%H:%M:%SZ"), "status": "ok", "origin": origin,
              "description": description, "sources": list(sources), "notes": list(notes), "inputs": [],
              "files": files}
    (d / "run.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (d / "log.txt").write_text(f"{slug}/{run_id}: imported {len(files)} file(s)\n", encoding="utf-8")
    return d, record
