"""From a run to a version, and rendering the -meta of a version (decision 0018).

add-version <slug>/<run-id> …: refuses runs that failed, ran uncommitted code or used runs as inputs (except runs
of the same call, which become versions together: the authority datasets); gives the
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
    lines += [f"{k} = {toml_value(v[k])}" for k in ("version", "issued", "author", "commit", "description",
                                                   "withdrawn") if v.get(k) is not None]
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


def add_version(cfg, slug, run_id, version=None, author=None, description=None, text=None, issued=None,
                dry_run=False, log=print):
    """Make a run a version. Returns (version id, directory, the version table, warnings)."""
    return add_versions(cfg, [(slug, run_id)], version, author, description, text, issued, dry_run, log)[0]


def add_versions(cfg, items, version=None, author=None, description=None, text=None, issued=None, dry_run=False,
                 log=print):
    """Make several runs versions together: [(slug, run id)]. A run may read another run of the list (the authority
    datasets, which select from each other); its run record then names the version that run becomes, with the
    checksums of its files in the version (the same triples; the version adds header comments). Returns
    [(version id, directory, the version table, warnings)]."""
    cat = catalog.Catalog()
    if len({s for s, _ in items}) != len(items):
        raise VersionError("one run per dataset")
    batch = dict(items)
    store = cfg.require("store")
    commit, dirty = framework_state()
    if dirty and not dry_run:
        raise VersionError(f"the framework has uncommitted changes ({', '.join(dirty)}); the -meta names its commit")
    registry = Registry()
    author = author or git_user()
    if not author:
        raise VersionError("no author (--author, or git config user.name)")
    registry.number(author)
    if issued and not catalog.is_date(issued):
        raise VersionError(f"--issued {issued}: not a date")

    jobs = []
    for slug, run_id in items:
        e, run, rec = check_run(cfg, cat, slug, run_id, batch)
        vid = version or default_version(e, store, slug, run)
        if not catalog.SLUG.match(vid) or vid in catalog.RESERVED_VERSIONS:
            raise VersionError(f"'{vid}' is not a valid version id")
        if e.version(vid) or (store / slug / vid).exists() or runs.record_path(slug, vid).exists():
            raise VersionError(f"version {slug}/{vid} exists already")
        jobs.append({"slug": slug, "run_id": run_id, "e": e, "run": run, "rec": copy.deepcopy(rec), "vid": vid})

    try:
        for j in jobs:
            stage_files(cfg, j, dry_run)
        version_of = {j["slug"]: j for j in jobs}
        for j in jobs:
            relink(j, version_of)
        for j in jobs:
            prepare(cfg, j, author, description, text, issued, registry, commit)
    except BaseException:
        for j in jobs:
            if j.get("stage"):
                shutil.rmtree(j["stage"], ignore_errors=True)
        raise
    return [finish(j, dry_run) for j in jobs]


def check_run(cfg, cat, slug, run_id, batch=None):
    """The entry, run and run record; refuses what cannot become a version. batch: {slug: run id} of the call. An
    input may be a run of a dataset of the batch: its run there, or another run with the same file (when the cascade
    of the authority datasets has converged, the last runs read the runs before them)."""
    batch = batch or {}
    e = cat.get(slug)
    if e is None:
        raise VersionError(f"no dataset '{slug}' in the catalogue")
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
            s, r, path = (ref.split("/", 2) + [""])[:3]
            if s not in batch:
                raise VersionError(f"input {i.get('name')} is a run ({ref}); make it a version first, or together")
            if r != batch[s]:
                other = runs.get_run(cfg.require("build"), s, batch[s])
                same = other and other["record"] and any(
                    f["path"] == path and f["sha256"] == i.get("sha256") for f in other["record"].get("files", []))
                if not same:
                    raise VersionError(f"input {i.get('name')} ({ref}) differs from {s}/{batch[s]} of this call: "
                                       f"run {slug} again with --use {s}/{batch[s]}")
    became = runs.version_of_run(slug, run_id)
    if became:
        raise VersionError(f"{slug}/{run_id} is already the version {became}")
    return e, run, rec


def stage_files(cfg, j, dry_run):
    """Copy the files of the run into a staging directory, with the header comments; checked against the record."""
    slug, run, rec, vid = j["slug"], j["run"], j["rec"], j["vid"]
    files = [dict(f) for f in rec.get("files", [])]
    if meta.meta_path(slug) in {f["path"] for f in files}:
        raise VersionError(f"the run wrote {meta.meta_path(slug)}; the -meta is rendered by the framework")
    for f in files:
        local = run["dir"] / f["path"]
        if not local.is_file() or catalog.sha256(local) != f["sha256"]:
            raise VersionError(f"{f['path']} in the run directory differs from the run record")
    target = cfg.require("store") / slug / vid
    if dry_run:
        target = cfg.require("build") / slug / f"{j['run_id']}-as-{vid}"
        if target.exists():
            shutil.rmtree(target)
    stage = target.with_name(f".{target.name}.tmp")
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    j.update(stage=stage, target=target)
    for f in files:
        dst = stage / f["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(run["dir"] / f["path"], dst)
        if rec.get("mode") != "import" and "triples" in f and rdf.rdf_format(f["path"]) == "turtle":
            # written by the generator (imported files and copied inputs keep their bytes)
            f.update(turtle.add_header(dst, meta.header(slug, vid)))
    j["files"] = files


def relink(j, version_of):
    """The inputs, --use and authority links of the run record that are runs of datasets of the batch: the versions
    these datasets get (check_run made sure the files are the same)."""
    rec = j["rec"]
    for i in rec.get("inputs", []):
        ref = i.get("ref")
        if not isinstance(ref, str) or ref.startswith("repo:"):
            continue
        parts = ref.split("/", 2)
        other = version_of.get(parts[0]) if len(parts) > 1 and runs.is_run_id(parts[1]) else None
        if other is None:
            continue
        f = next((x for x in other["files"] if x["path"] == (parts[2] if len(parts) > 2 else "")), None)
        i["ref"] = "/".join([other["slug"], other["vid"]] + parts[2:])
        i["read_as"] = ref   # the run read the run's file, which the version holds with header comments
        if f:
            i["sha256"], i["bytes"] = f["sha256"], f["bytes"]
    for s, v in list(rec.get("use", {}).items()):
        if s in version_of and runs.is_run_id(v):
            rec["use"][s] = version_of[s]["vid"]
    for s, info in rec.get("authority_links", {}).items():
        sel = info.get("selection")
        if sel and s in version_of and runs.is_run_id(sel.split("/")[1]):
            info["selection"] = f"{s}/{version_of[s]['vid']}"


def prepare(cfg, j, author, description, text, issued, registry, commit):
    """The -meta (in the staging directory), the catalogue entry and the run record of the version, not written."""
    slug, e, rec, vid, files, stage = (j[k] for k in ("slug", "e", "rec", "vid", "files", "stage"))
    warnings = []
    for i in rec.get("inputs", []):
        if not isinstance(i.get("ref"), str):
            warnings.append(f"input {i.get('name')} ({i.get('file')}) is named by checksum only, not in the inputs "
                            "area (decision 0021)")
    stats = measure(cfg, files, stage)
    public = [{k: f.get(k) for k in ("path", "bytes", "sha256", "triples")} for f in files]
    vtable = {"version": vid, "issued": issued or rec["started"][:10], "author": author, "commit": rec["commit"]}
    if description:
        vtable["description"] = description
    m = write_meta(stage / meta.meta_path(slug), e, vtable, public, rec, stats, registry, commit)
    vtable["files"] = [{k: v for k, v in f.items() if v is not None} for f in public] + [m]
    change = {"date": datetime.date.today().isoformat(), "version": vid, "author": author,
              "text": text or (f"New version, imported ({j['run_id']})." if rec.get("mode") == "import" else
                               f"New version, made by the generator in judaicalink-data ({j['run_id']}).")}
    entry_text = add_version_text(e.path.read_text(encoding="utf-8"), e.data, vtable, change)
    record = dict(rec)
    record["version"] = vid
    record["files"] = files
    record_text = json.dumps(record, indent=1, ensure_ascii=False) + "\n"
    j.update(vtable=vtable, warnings=warnings, entry_text=entry_text, record_text=record_text)


def finish(j, dry_run):
    """Move the staged version into place and write the run record and the catalogue entry."""
    slug, e, run, vid, files, stage, target = (j[k] for k in ("slug", "e", "run", "vid", "files", "stage", "target"))
    vtable, warnings, entry_text, record_text = (j[k] for k in ("vtable", "warnings", "entry_text", "record_text"))
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


# --- remove-version --------------------------------------------------------------------------------

def remove_version_text(text, data, vid):
    """The entry text without the version vid, its changelog entries and a stable pointer to it."""
    head, fm, tail = split_entry(text)
    lines = fm.split("\n")
    headers = [i for i, line in enumerate(lines) if re.match(r"^\[\[?[^\]]+\]\]?\s*$", line.strip())]

    def table_end(i):
        nxt = [h for h in headers if h > i and not re.match(r"^\s*\[\[versions\.files\]\]", lines[h])]
        return nxt[0] if nxt else len(lines)

    def has(i, key):
        j = i + 1
        while j < len(lines) and j not in headers:
            if re.match(rf"^\s*{key}\s*=\s*{re.escape(toml_value(vid))}\s*$", lines[j]):
                return True
            j += 1
        return False

    drop = set()
    for h in headers:
        if re.match(r"^\[\[versions\]\]", lines[h]) and has(h, "version"):
            drop.update(range(h, table_end(h)))
        elif re.match(r"^\[\[changelog\]\]", lines[h]) and has(h, "version"):
            drop.update(range(h, table_end(h)))
    lines = [line for i, line in enumerate(lines)
             if i not in drop and not re.match(rf"^stable\s*=\s*{re.escape(toml_value(vid))}\s*$", line)]
    expected = copy.deepcopy(data)
    expected["versions"] = [v for v in data.get("versions", []) if v.get("version") != vid]
    expected["changelog"] = [c for c in data.get("changelog", []) if c.get("version") != vid]
    for k in ("versions", "changelog"):
        if not expected[k]:
            del expected[k]
    if expected.get("stable") == vid:
        del expected["stable"]
    return checked(head + "\n".join(lines) + tail, expected)


def version_refs(rec):
    """The catalogued versions a run record names: its inputs and the corrections applied to them (decision 0023),
    as {(slug, version)}; inputs of the inputs area, runs and repository files are not versions."""
    out = set()
    for i in rec.get("inputs", []) + rec.get("corrections", []):
        ref = str(i.get("ref", ""))
        if ref.startswith(("inputs:", "repo:")):
            continue
        slug, _, rest = ref.partition("/")
        vid = rest.partition("/")[0]
        if slug and vid and not runs.is_run_id(vid):
            out.add((slug, vid))
    return out


def dependents(slug, vid, cat=None):
    """The versions made from slug/vid (named in their run records as an input or applied correction)."""
    cat = cat or catalog.Catalog()
    return sorted(f"{other.name}/{v.get('version')}" for other in cat.entries.values() for v in other.versions()
                  if (slug, vid) in version_refs(runs.version_record(other.name, v.get("version")) or {})
                  and (other.name, v.get("version")) != (slug, vid))


def latest_version(e):
    """The newest version of an entry: the latest issued date, then the highest version id."""
    vs = [v for v in e.versions() if isinstance(v.get("version"), str)]
    return max(vs, key=lambda v: (str(v.get("issued", "")), v["version"]))["version"] if vs else None


def remove_version(cfg, slug, vid, latest_ok=False, warn=print):
    """Remove a version that was never published: from the catalogue (version, its changelog entries, stable),
    the store, its run record and its run directory (decision 0018: one version per piece of work)."""
    e = catalog.Catalog().get(slug)
    if e is None or e.version(vid) is None:
        raise VersionError(f"no version {slug}/{vid} in the catalogue")
    if e.stable == vid:
        raise VersionError(f"{slug}/{vid} is the stable version, which is never removed (to replace an unpublished "
                           "stable version, set stable to another version or remove the stable line in the catalogue "
                           "first, deliberately)")
    if latest_version(e) == vid:
        warn(f"warning: {slug}/{vid} is the latest version of {slug}")
        if not latest_ok:
            raise VersionError(f"{slug}/{vid} is the latest version; remove it only if it is a development version "
                               "that was never used, and confirm with --latest")
    if (runs.version_record(slug, vid) or {}).get("mode") == "import":
        raise VersionError(f"{slug}/{vid} was imported from the published dumps (its run record has mode 'import'); "
                           "published versions are never removed")
    made_from = dependents(slug, vid)
    if made_from:
        raise VersionError(f"{', '.join(made_from)} made from {slug}/{vid} (input or applied correction); a version "
                           "that a later version was made from is not removed (remove those first)")
    entry_text = remove_version_text(e.path.read_text(encoding="utf-8"), e.data, vid)
    rec = runs.version_record(slug, vid) or {}
    e.path.write_text(entry_text, encoding="utf-8")
    store = cfg.require("store") / slug / vid
    if store.exists():
        shutil.rmtree(store)
    rp = runs.record_path(slug, vid)
    if rp.exists():
        rp.unlink()
    run_dir = cfg.require("build") / slug / rec["run"] if rec.get("run") else None
    if run_dir and run_dir.exists():
        shutil.rmtree(run_dir)
