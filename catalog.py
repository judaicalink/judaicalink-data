#!/usr/bin/env python3
"""Catalogue tooling for judaicalink-data (decisions 0013, 0014).

    python3 catalog.py check [--catalog DIR] [--dumps DIR ...] [--complete]
    python3 catalog.py collect --from DIR [--from DIR ...] --to DIR [--dry-run]

check   parses every entry in catalog/, checks the entry format of 0013 and reports errors and
        warnings; with --dumps, compares sizes and checksums with local copies of the files at
        DIR/<slug>/<version>/<path>; with --complete, each DIR must hold exactly the catalogued files.
        Exit status 1 if there are errors.
collect builds a dumps tree <slug>/<version>/<path> with the files of all catalogued versions: each file
        is looked up by size and sha256 in the --from directories (any layout) and hard-linked (copied
        if that fails) into --to. Files already in place are checked; files in --to that the catalogue
        does not name are reported, never deleted. Exit status 1 if a file is missing or differs.

Standard library only.
"""

import argparse
import datetime
import hashlib
import os
import re
import shutil
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "catalog"
DECISIONS = ROOT / "docs" / "decisions"

SLUG = re.compile(r"^[a-z0-9][a-z0-9.-]*$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}")
FRONT_MATTER = re.compile(r"^﻿?\+\+\+[ \t]*\r?\n(.*?)\r?\n\+\+\+[ \t]*(?:\r?\n|$)", re.S)

KINDS = {"records", "complement", "linkset", "entity-pages", "ontology", "vocabulary", "support"}
METHODS = {"curated", "scraped", "converted", "deterministic", "rule-based", "lookup", "statistical",
           "ai-generated"}


# --- reading -------------------------------------------------------------------------------------

class Entry:
    def __init__(self, path, data, body):
        self.path = path
        self.data = data
        self.body = body

    @property
    def name(self):
        return self.path.stem

    def versions(self):
        v = self.data.get("versions", [])
        return [x for x in v if isinstance(x, dict)] if isinstance(v, list) else []


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


# --- check ---------------------------------------------------------------------------------------

class Report:
    def __init__(self):
        self.errors = 0
        self.warnings = 0

    def error(self, where, msg):
        self.errors += 1
        print(f"{where}: error: {msg}")

    def warn(self, where, msg):
        self.warnings += 1
        print(f"{where}: warning: {msg}")


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
           "graph": URL, "description": TEXT, "withdrawn": TEXT, "files": (lambda v: True, "")}

# Dataset fields; tables and lists of tables are checked separately.
DATASET = {
    "slug": (lambda v: isinstance(v, str) and SLUG.match(v), "a slug (lower-case letters, digits, '-', '.')"),
    "title": TEXT, "author": AUTHOR, "license": (lambda v: True, ""),
    "date": DATE, "website": URL, "links": (lambda v: True, ""), "example": URL, "picture": TEXT,
    "kind": (lambda v: v in KINDS, "one of " + ", ".join(sorted(KINDS))),
    "method": (lambda v: isinstance(v, list) and v and all(x in METHODS for x in v),
               "a non-empty list of " + ", ".join(sorted(METHODS))),
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
        else:
            v = next(v for v in e.versions() if v.get("version") == stable)
            if "withdrawn" in v:
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


def cmd_check(args):
    r = Report()
    entries = []
    for path in entry_files(args.catalog):
        try:
            entries.append(read_entry(path))
        except ValueError as e:
            r.error(path.name, str(e))
    slugs = {e.name for e in entries}
    decisions = {p.name[:4] for p in DECISIONS.glob("[0-9][0-9][0-9][0-9]-*.md")}
    for e in entries:
        check_entry(r, e, slugs, decisions)
        if args.dumps:
            check_local_files(r, e, args.dumps, args.complete)
    if args.dumps and args.complete:
        named = {f"{e.name}/{v.get('version')}/{f.get('path')}" for e in entries for v in e.versions()
                 for f in v.get("files", []) if isinstance(f, dict)}
        for root in args.dumps:
            for p in sorted(root.rglob("*")):
                if p.is_file() and p.relative_to(root).as_posix() not in named:
                    r.error(str(root), f"{p.relative_to(root).as_posix()} is not in the catalogue")
    print(f"{len(entries)} entries, {r.errors} errors, {r.warnings} warnings", file=sys.stderr)
    return 1 if r.errors else 0


def cmd_collect(args):
    entries = [read_entry(p) for p in entry_files(args.catalog)]
    wanted = {}  # relative path in the tree -> (bytes, sha256)
    for e in entries:
        for v in e.versions():
            for f in v.get("files", []):
                wanted[f"{e.name}/{v['version']}/{f['path']}"] = (f.get("bytes"), f.get("sha256"))
    sizes = {b for b, _ in wanted.values()}
    by_size = {}  # bytes -> files in the source directories with that size
    for root in args.sources:
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
        target = args.to / rel
        if not sha:
            print(f"{rel}: no sha256 in the catalogue, skipped")
            missing += 1
            continue
        if target.exists():
            if target.stat().st_size == size and digest(target) == sha:
                present += 1
            else:
                print(f"{rel}: differs from the catalogue")
                missing += 1
            continue
        source = next((p for p in by_size.get(size, []) if digest(p) == sha), None)
        if source is None:
            print(f"{rel}: not found in the source directories")
            missing += 1
            continue
        linked += 1
        if args.dry_run:
            print(f"{rel} <- {source}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(source, target)
        except OSError:
            shutil.copy2(source, target)
    if args.to.exists():
        for dirpath, _, names in os.walk(args.to):
            for n in names:
                rel = (Path(dirpath) / n).relative_to(args.to).as_posix()
                if rel not in wanted:
                    print(f"{rel}: in the tree but not in the catalogue")
    verb = "to link" if args.dry_run else "linked"
    print(f"{len(wanted)} files: {present} in place, {linked} {verb}, {missing} missing or different",
          file=sys.stderr)
    return 1 if missing else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("check", help="check the catalogue entries (format of decision 0013)")
    p.add_argument("--catalog", metavar="DIR", type=Path, default=CATALOG,
                   help="catalogue directory (default: catalog/ of this repository)")
    p.add_argument("--dumps", metavar="DIR", type=Path, action="append", default=[],
                   help="local dump directory with <slug>/<version>/<path>; repeatable")
    p.add_argument("--complete", action="store_true",
                   help="each --dumps directory must hold exactly the catalogued files (no file missing, none extra)")
    p.set_defaults(func=cmd_check)
    p = sub.add_parser("collect", help="build a dumps tree <slug>/<version>/<path> from local files")
    p.add_argument("--catalog", metavar="DIR", type=Path, default=CATALOG,
                   help="catalogue directory (default: catalog/ of this repository)")
    p.add_argument("--from", dest="sources", metavar="DIR", type=Path, action="append", required=True,
                   help="directory to take files from (any layout, found by size and sha256); repeatable")
    p.add_argument("--to", metavar="DIR", type=Path, required=True, help="the tree to build")
    p.add_argument("--dry-run", action="store_true", help="only report what would be linked")
    p.set_defaults(func=cmd_collect)
    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
