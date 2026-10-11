"""The catalogue: reading the entries, derived values, the check, and collecting the store (decisions 0013,
0014, 0015, 0018, 0019).

An entry is catalog/<slug>.md, TOML front matter between +++ lines and a Markdown body. Values that the
tooling derives (replaced_by, used_by, contributors, the status of a version) are never stored in entries.
"""

import datetime
import hashlib
import json
import os
import re
import shutil
import tomllib
from pathlib import Path

from .config import CATALOG, DECISIONS, GENERATORS

SLUG = re.compile(r"^[a-z0-9][a-z0-9.-]*$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}")
FRONT_MATTER = re.compile(r"^﻿?\+\+\+[ \t]*\r?\n(.*?)\r?\n\+\+\+[ \t]*(?:\r?\n|$)", re.S)

RESERVED_SLUGS = {"agents"}                # datasets/agents/… holds the agents (0018)
RESERVED_VERSIONS = {"meta", "current"}    # datasets/<slug>/meta, <slug>/current (0018)


# --- reading -------------------------------------------------------------------------------------

def as_list(v):
    """A name or a list of names as a list."""
    if isinstance(v, str):
        return [v]
    return [x for x in v if isinstance(x, str)] if isinstance(v, list) else []


class Entry:
    def __init__(self, path, data, body):
        self.path = path
        self.data = data
        self.body = body

    @property
    def name(self):
        return self.path.stem

    @property
    def title(self):
        return self.data.get("title", "")

    @property
    def stable(self):
        s = self.data.get("stable")
        return s if isinstance(s, str) else None

    def versions(self):
        v = self.data.get("versions", [])
        return [x for x in v if isinstance(x, dict)] if isinstance(v, list) else []

    def version(self, vid):
        return next((v for v in self.versions() if v.get("version") == vid), None)

    def changelog(self):
        c = self.data.get("changelog", [])
        return [x for x in c if isinstance(x, dict)] if isinstance(c, list) else []

    def status(self, vid):
        """stable, preview (listed above stable, or no stable at all), older (below stable), withdrawn."""
        v = self.version(vid)
        if v is None:
            return None
        if "withdrawn" in v:
            return "withdrawn"
        if self.stable is None:
            return "preview"
        if vid == self.stable:
            return "stable"
        ids = [x.get("version") for x in self.versions()]
        return "preview" if self.stable in ids and ids.index(vid) < ids.index(self.stable) else "older"

    def summary(self):
        """The part of the body before <!--more--> as plain text."""
        text = self.body.split("<!--more-->")[0]
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
        return re.sub(r"\s+", " ", text).strip()

    def description(self):
        """The full body as written (Markdown), without the <!--more--> marker."""
        text = "\n".join(line.rstrip() for line in self.body.replace("\r\n", "\n").split("\n"))
        return "\n\n".join(p.strip() for p in text.split("<!--more-->") if p.strip())

    def contributors(self):
        """Everyone named as author of a version or a changelog entry (0013), sorted by name."""
        names = set()
        for v in self.versions():
            names.update(as_list(v.get("author")))
        for c in self.changelog():
            names.update(as_list(c.get("author")))
        return sorted(names)

    def file_description(self, path, version=None):
        if version is not None:
            for f in version.get("files", []):
                if isinstance(f, dict) and f.get("path") == path and isinstance(f.get("description"), str):
                    return f["description"]
        files = self.data.get("files")
        return files.get(path) if isinstance(files, dict) else None


def entry_files(catalog=CATALOG):
    """Entry files: every *.md in the catalogue except README.md and Hugo's _index.md."""
    return sorted(p for p in catalog.glob("*.md") if p.name != "README.md" and not p.name.startswith("_"))


def read_entry(path):
    """Return an Entry, or raise ValueError if the front matter is missing or not valid TOML."""
    text = path.read_text(encoding="utf-8")
    m = FRONT_MATTER.match(text)
    if not m:
        raise ValueError("no TOML front matter between +++ lines")
    try:
        data = tomllib.loads(m.group(1))
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"invalid TOML: {e}") from None
    return Entry(path, data, text[m.end():])


class Catalog:
    """All entries, with the values derived across entries."""

    def __init__(self, catalog=None):
        catalog = catalog or CATALOG
        self.dir = catalog
        self.entries = {}
        self.errors = {}   # file name -> reason it could not be read
        for path in entry_files(catalog):
            try:
                e = read_entry(path)
                self.entries[e.name] = e
            except ValueError as err:
                self.errors[path.name] = str(err)

    def get(self, slug):
        return self.entries.get(slug)

    def replaced_by(self, slug):
        return sorted(s for s, e in self.entries.items() if slug in as_list(e.data.get("replaces")))

    def used_by(self, slug):
        return sorted(s for s, e in self.entries.items() if slug in as_list(e.data.get("inputs")))

    def names(self):
        """Every person named in the catalogue -> the slugs that name them (author, versions, changelog)."""
        out = {}
        for s, e in self.entries.items():
            for n in as_list(e.data.get("author")) + e.contributors():
                out.setdefault(n, set()).add(s)
        return {n: sorted(v) for n, v in sorted(out.items())}


def generator_folder(slug):
    """What the generator folder holds: README, original/, generate.py, run records."""
    d = GENERATORS / slug
    return {"folder": d.is_dir(), "readme": (d / "README.md").is_file(), "original": (d / "original").is_dir(),
            "generate": (d / "generate.py").is_file(),
            "run_records": sorted(p.stem for p in (d / "runs").glob("*.json")) if (d / "runs").is_dir() else []}


# --- check ---------------------------------------------------------------------------------------

class Report:
    def __init__(self, out=print):
        self.errors = 0
        self.warnings = 0
        self.out = out

    def error(self, where, msg):
        self.errors += 1
        self.out(f"{where}: error: {msg}")

    def warn(self, where, msg):
        self.warnings += 1
        self.out(f"{where}: warning: {msg}")


def is_str(v):
    return isinstance(v, str) and v.strip() != ""


def as_date(v):
    if isinstance(v, datetime.datetime):
        return v.date()
    if isinstance(v, datetime.date):
        return v
    try:
        return datetime.date.fromisoformat(v[:10]) if ISO_DATE.match(v) else None
    except (TypeError, ValueError):
        return None


def is_date(v):
    return as_date(v) is not None


def is_url(v):
    return isinstance(v, str) and re.match(r"^https?://\S+$", v)


def is_str_list(v):
    return isinstance(v, list) and all(is_str(x) for x in v)


def check_table(r, where, value, fields, required=()):
    """Check a table against {field: (test, description)}; unknown fields are warnings."""
    if not isinstance(value, dict):
        r.error(where, "must be a table")
        return
    for f in required:
        if f not in value:
            r.error(where, f"missing required field '{f}'")
    for f, v in value.items():
        if f not in fields:
            r.warn(where, f"unknown field '{f}'")
        elif not fields[f][0](v):
            r.error(where, f"'{f}' must be {fields[f][1]}")


TEXT = (is_str, "a non-empty string")
URL = (is_url, "an http(s) URL")
DATE = (is_date, "a date (YYYY-MM-DD...)")
SLUGS = (lambda v: isinstance(v, list) and all(isinstance(x, str) and SLUG.match(x) for x in v),
         "a list of slugs")
COUNT = (lambda v: isinstance(v, int) and not isinstance(v, bool) and v >= 0, "a non-negative integer")

AUTHOR = (lambda v: is_str(v) or (is_str_list(v) and len(v) > 0), "a name or a list of names")
LICENSE = {"name": TEXT, "uri": URL, "image": URL}
LINK = {"url": URL, "label": TEXT}
GENERATOR = {"repo": URL, "path": TEXT}
FILE = {"path": TEXT, "description": TEXT, "bytes": COUNT,
        "sha256": (lambda v: isinstance(v, str) and re.match(r"^[0-9a-f]{64}$", v), "64 hex digits"),
        "triples": COUNT}
CHANGE = {"date": DATE, "text": TEXT, "version": TEXT, "author": AUTHOR,
          "refs": (lambda v: isinstance(v, list) and all(isinstance(x, str) and re.match(r"^\d{4}$", x)
                                                          for x in v), "a list of decision numbers")}

# Fields of a version other than files (checked separately).
VERSION = {"version": (lambda v: isinstance(v, str) and SLUG.match(v),
                       "a slug (lower-case letters, digits, '-', '.')"),
           "issued": DATE, "author": AUTHOR,
           "commit": (lambda v: isinstance(v, str) and re.match(r"^[0-9a-f]{7,40}$", v), "a commit hash"),
           "description": TEXT, "withdrawn": TEXT, "files": (lambda v: True, "")}

# Dataset fields; tables and lists of tables are checked separately.
DATASET = {
    "slug": (lambda v: isinstance(v, str) and SLUG.match(v), "a slug (lower-case letters, digits, '-', '.')"),
    "title": TEXT, "author": AUTHOR, "license": (lambda v: True, ""),
    "date": DATE, "website": URL, "links": (lambda v: True, ""), "example": URL, "picture": TEXT,
    "kind": (lambda v: isinstance(v, str), "a value of catalog/vocabulary.toml"),   # values: check_vocabulary
    "method": (lambda v: isinstance(v, list) and v and all(isinstance(x, str) for x in v),
               "a non-empty list of values of catalog/vocabulary.toml"),
    "namespaces": (lambda v: is_str_list(v) and all(not x.startswith("/") and not x.startswith("http")
                                                    for x in v),
                   "a list of namespaces relative to http://data.judaicalink.org/data/"),
    "replaces": SLUGS, "inputs": SLUGS, "generator": (lambda v: True, ""), "stable": TEXT,
    "withdrawn": TEXT,
    "aliases": (lambda v: is_str_list(v) and all(x.startswith("/") for x in v), "a list of paths starting with /"),
    "files": (lambda v: True, ""), "versions": (lambda v: True, ""),
    "changelog": (lambda v: True, ""),
}
REQUIRED = ("slug", "title", "author", "license")


def check_list_of_tables(r, where, value, fields, required=()):
    if not isinstance(value, list):
        r.error(where, "must be a list of tables")
        return []
    for i, t in enumerate(value, 1):
        check_table(r, f"{where}[{i}]", t, fields, required)
    return [t for t in value if isinstance(t, dict)]


def check_entry(r, e, slugs, decisions):
    d, where = e.data, e.path.name
    check_table(r, where, d, DATASET, REQUIRED)
    if isinstance(d.get("slug"), str) and d["slug"] != e.name:
        r.error(where, f"slug '{d['slug']}' differs from the file name '{e.name}'")
    if e.name in RESERVED_SLUGS:
        r.error(where, f"'{e.name}' is a reserved slug (0018)")

    if "license" in d:
        check_table(r, f"{where} license", d["license"], LICENSE, ("name",))
    if "links" in d:
        check_list_of_tables(r, f"{where} links", d["links"], LINK, ("url",))
    if "generator" in d:
        check_table(r, f"{where} generator", d["generator"], GENERATOR, ("repo", "path"))
    for f in ("replaces", "inputs"):
        for s in d.get(f, []) if isinstance(d.get(f), list) else []:
            if s == e.name:
                r.error(where, f"'{f}' names the dataset itself")
            elif s not in slugs:
                r.error(where, f"'{f}' names '{s}', which is not in the catalogue")

    # versions
    ids, used_paths, previous = [], set(), None
    if "versions" in d:
        for i, v in enumerate(check_list_of_tables(r, f"{where} versions", d["versions"], VERSION,
                                                   ("version",)), 1):
            vid = v.get("version")
            vwhere = f"{where} version {vid}" if isinstance(vid, str) else f"{where} versions[{i}]"
            if isinstance(vid, str):
                if vid in ids:
                    r.error(vwhere, "version id is not unique")
                if vid in RESERVED_VERSIONS:
                    r.error(vwhere, f"'{vid}' is a reserved version id (0018)")
                ids.append(vid)
            issued = as_date(v.get("issued"))
            if issued and previous and issued > previous:
                r.warn(vwhere, "issued later than the version above it (versions are listed newest first)")
            previous = issued or previous
            paths = set()
            for j, f in enumerate(check_list_of_tables(r, f"{vwhere} files", v.get("files", []), FILE,
                                                       ("path",)), 1):
                p = f.get("path")
                if not isinstance(p, str):
                    continue
                if p.startswith("/") or "\\" in p or any(part in ("", ".", "..") for part in p.split("/")):
                    r.error(f"{vwhere} files[{j}]", f"path '{p}' must be relative to <slug>/<version>/")
                if p in paths:
                    r.error(f"{vwhere} files[{j}]", f"path '{p}' is listed twice")
                paths.add(p)
            used_paths |= paths

    stable = d.get("stable")
    if isinstance(stable, str):
        if stable not in ids:
            r.error(where, f"stable version '{stable}' is not among the versions")
        elif "withdrawn" in e.version(stable):
            r.warn(where, f"stable version '{stable}' is withdrawn")

    # [files] descriptions
    if "files" in d:
        if isinstance(d["files"], dict):
            for p, text in d["files"].items():
                if not is_str(text):
                    r.error(f"{where} files", f"description of '{p}' must be a non-empty string")
                if p not in used_paths:
                    r.warn(f"{where} files", f"description of '{p}', which no version lists")
        else:
            r.error(f"{where} files", "must be a table path = description"
                    + (" (old format: [[files]] with url)" if isinstance(d["files"], list) else ""))

    # changelog
    if "changelog" in d:
        for i, c in enumerate(check_list_of_tables(r, f"{where} changelog", d["changelog"], CHANGE,
                                                   ("date", "text")), 1):
            if isinstance(c.get("version"), str) and c["version"] not in ids:
                r.warn(f"{where} changelog[{i}]", f"version '{c['version']}' is not among the versions")
            for ref in c.get("refs", []) if isinstance(c.get("refs"), list) else []:
                if isinstance(ref, str) and re.match(r"^\d{4}$", ref) and ref not in decisions:
                    r.warn(f"{where} changelog[{i}]", f"decision {ref} does not exist")


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def check_local_files(r, e, dumps, complete=False):
    """Compare bytes and sha256 of each version file with local copies under the dump directories;
    with complete, a file missing from a dump directory is an error."""
    for v in e.versions():
        vid = v.get("version")
        files = v.get("files", [])
        if not isinstance(vid, str) or not isinstance(files, list):
            continue
        for f in files:
            if not isinstance(f, dict) or not isinstance(f.get("path"), str):
                continue
            rel = f"{e.name}/{vid}/{f['path']}"
            for root in dumps:
                local = root / rel
                where = f"{e.path.name} {rel}"
                if not local.is_file():
                    if complete:
                        r.error(where, f"missing in {root}")
                    continue
                size = local.stat().st_size
                if isinstance(f.get("bytes"), int) and f["bytes"] != size:
                    r.error(where, f"{f['bytes']} bytes in the entry, {size} in {root}")
                elif isinstance(f.get("sha256"), str) and f["sha256"] != sha256(local):
                    r.error(where, f"sha256 differs from the copy in {root}")


def check_vocabulary(r, cat):
    """kind and method use the values of catalog/vocabulary.toml (0013, 0018)."""
    from . import vocabulary
    try:
        allowed = {f: vocabulary.values(f) for f in vocabulary.FIELDS}
    except ValueError as e:
        r.error("vocabulary.toml", str(e))
        return
    for e in cat.entries.values():
        for f in vocabulary.FIELDS:
            v = e.data.get(f)
            for x in ([v] if isinstance(v, str) else v if isinstance(v, list) else []):
                if isinstance(x, str) and x not in allowed[f]:
                    r.error(e.path.name, f"{f} '{x}' is not one of {', '.join(sorted(allowed[f]))}")


def check_agents(r, cat, registry):
    """Every name in the catalogue is in the agents registry (0018)."""
    for err in registry.errors:
        r.error(registry.path.name, err)
    for name, slugs in cat.names().items():
        try:
            registry.number(name)
        except LookupError:
            r.error(registry.path.name, f"'{name}' (named in {', '.join(slugs)}) is not registered")


def check(catalog=CATALOG, dumps=(), complete=False, out=print, registry=None):
    """Check all entries (format of 0013, reserved names of 0018), the agents registry; with dumps, the local
    copies. Returns (entries, errors, warnings)."""
    from .agents import Registry
    registry = registry or Registry()
    r = Report(out)
    cat = Catalog(catalog)
    for name, err in cat.errors.items():
        r.error(name, err)
    decisions = {p.name[:4] for p in DECISIONS.glob("[0-9][0-9][0-9][0-9]-*.md")}
    for e in cat.entries.values():
        check_entry(r, e, set(cat.entries), decisions)
        if dumps:
            check_local_files(r, e, dumps, complete)
    check_agents(r, cat, registry)
    check_vocabulary(r, cat)
    if dumps and complete:
        named = {f"{e.name}/{v.get('version')}/{f.get('path')}" for e in cat.entries.values() for v in e.versions()
                 for f in v.get("files", []) if isinstance(f, dict)}
        for root in dumps:
            for p in sorted(root.rglob("*")):
                if p.is_file() and p.relative_to(root).as_posix() not in named:
                    r.error(str(root), f"{p.relative_to(root).as_posix()} is not in the catalogue")
    return len(cat.entries), r.errors, r.warnings


# --- collect -------------------------------------------------------------------------------------

def collect(sources, to, catalog=CATALOG, dry_run=False, out=print):
    """Build a tree <slug>/<version>/<path> with the files of all catalogued versions: each file is looked
    up by size and sha256 in the source directories (any layout) and hard-linked (copied if that fails).
    Files already in place are checked; files in the tree that the catalogue does not name are reported,
    never deleted. Returns (wanted, present, linked, missing)."""
    cat = Catalog(catalog)
    wanted = {}  # relative path in the tree -> (bytes, sha256)
    for e in cat.entries.values():
        for v in e.versions():
            for f in v.get("files", []):
                wanted[f"{e.name}/{v['version']}/{f['path']}"] = (f.get("bytes"), f.get("sha256"))
    sizes = {b for b, _ in wanted.values()}
    by_size = {}  # bytes -> files in the source directories with that size
    for root in sources:
        for dirpath, _, names in os.walk(root):
            for n in names:
                p = Path(dirpath) / n
                if not p.is_symlink() and p.stat().st_size in sizes:
                    by_size.setdefault(p.stat().st_size, []).append(p)
    hashes = {}

    def digest(p):
        if p not in hashes:
            hashes[p] = sha256(p)
        return hashes[p]

    missing = linked = present = 0
    for rel, (size, sha) in sorted(wanted.items()):
        target = to / rel
        if not sha:
            out(f"{rel}: no sha256 in the catalogue, skipped")
            missing += 1
            continue
        if target.exists():
            if target.stat().st_size == size and digest(target) == sha:
                present += 1
            else:
                out(f"{rel}: differs from the catalogue")
                missing += 1
            continue
        source = next((p for p in by_size.get(size, []) if digest(p) == sha), None)
        if source is None:
            out(f"{rel}: not found in the source directories")
            missing += 1
            continue
        linked += 1
        if dry_run:
            out(f"{rel} <- {source}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(source, target)
        except OSError:
            shutil.copy2(source, target)
    if to.exists():
        for dirpath, _, names in os.walk(to):
            for n in names:
                rel = (Path(dirpath) / n).relative_to(to).as_posix()
                if rel not in wanted:
                    out(f"{rel}: in the tree but not in the catalogue")
    return len(wanted), present, linked, missing
