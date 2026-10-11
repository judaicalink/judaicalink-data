"""Runs in the build area and the run records of versions (decision 0018).

A run is <build>/<slug>/<run-id>/ with the output files, run.json (the run record) and log.txt; the run id
is "run-" and a UTC timestamp. When a run becomes a version, its run record is copied to
generators/<slug>/runs/<version>.json in this repository.
"""

import json
import re
import shutil

from .config import GENERATORS

RUN_ID = re.compile(r"^run-\d{8}T\d{6}Z$")


def is_run_id(s):
    return bool(RUN_ID.match(s or ""))


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {"_error": f"{path.name}: {e}"}


def list_runs(build, slug):
    """The runs of a dataset in the build area, oldest first: [{id, dir, record}]."""
    d = build / slug if build else None
    if d is None or not d.is_dir():
        return []
    runs = []
    for p in sorted(d.iterdir()):
        if p.is_dir() and is_run_id(p.name):
            rec = p / "run.json"
            runs.append({"id": p.name, "dir": p, "record": read_json(rec) if rec.is_file() else None})
    return runs


def get_run(build, slug, run_id):
    return next((r for r in list_runs(build, slug) if r["id"] == run_id), None)


def version_record(slug, version):
    """The run record of a version, or None."""
    p = record_path(slug, version)
    return read_json(p) if p.is_file() else None


def record_path(slug, version):
    return GENERATORS / slug / "runs" / f"{version}.json"


def version_of_run(slug, run_id):
    """The version a run became, if any (the run record of that version names the run)."""
    d = GENERATORS / slug / "runs"
    if not d.is_dir():
        return None
    for p in sorted(d.glob("*.json")):
        if read_json(p).get("run") == run_id:
            return p.stem
    return None


def log_tail(run, lines=10):
    p = run["dir"] / "log.txt"
    if not p.is_file():
        return []
    return p.read_text(encoding="utf-8", errors="replace").splitlines()[-lines:]


def clean(build, slugs=None, dry_run=False):
    """Delete the runs (and add-version dry-run previews) in the build area that did not become a version; the run
    of a version keeps its directory (record and log). Returns the deleted directories."""
    if build is None or not build.is_dir():
        return []
    gone = []
    for d in sorted(build.iterdir()):
        if not d.is_dir() or d.name.startswith(".") or (slugs and d.name not in slugs):
            continue
        for r in sorted(d.iterdir()):
            run_id = r.name.split("-as-")[0]
            if not r.is_dir() or not is_run_id(run_id):
                continue
            if "-as-" not in r.name and version_of_run(d.name, run_id):
                continue
            gone.append(r)
            if not dry_run:
                shutil.rmtree(r)
    return gone
