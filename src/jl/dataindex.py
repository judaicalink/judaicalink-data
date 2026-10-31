"""The data index and the copy of the catalogue into the sites (decision 0014).

update(): checks every file of every version at every dumps location of catalog/locations.toml and every dataset
at every catalogue (HTTP HEAD, following redirects), and returns the index: when it was checked, the locations,
and per dataset its title, stable version, replaces/replaced_by, the catalogues that list it, and its versions
(newest first) with their files and the dumps locations where each was found. Only what was found somewhere is in
the index: a dataset if a catalogue lists it or a file of it was found, a version if a file of it was found.

sync(): copies the entries that a site already has (content/datasets/<slug>.md) and the index (data/dataindex.json)
into a Hugo site, with the labels of kinds and methods (data/catalogvocabulary.json); it adds entries only when
they are named explicitly and never removes any.
"""

import datetime
import json
import shutil
import time
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

from . import fetch
from .catalog import Catalog, as_list
from .config import CATALOG

LOCATIONS = CATALOG / "locations.toml"
INDEX = CATALOG / "dataindex.json"
COPY_NOTE = ("<!-- Copy of catalog/{slug}.md of https://github.com/judaicalink/judaicalink-data "
             "(jl sync-site); change it there. -->\n")


def locations(path=LOCATIONS):
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return {"dumps": dict(data.get("dumps", {})), "catalogues": dict(data.get("catalogues", {}))}


def probe(url, pause=0.3):
    """(found, size or None) for a URL: HEAD, redirects followed, found if the last answer is 200."""
    time.sleep(pause)
    try:
        with urllib.request.urlopen(fetch.request(url, method="HEAD"), timeout=30) as r:
            size = r.headers.get("Content-Length")
            return r.status == 200, int(size) if size and size.isdigit() else None
    except urllib.error.HTTPError as e:
        return False, None
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        return False, None


def quote(path):
    return urllib.request.quote(path, safe="/")


def update(assume=None, out=print, pause=0.3):
    """The index. assume: {dumps location: local directory} to take a local tree as the content of a location
    (for testing the sites before a location is filled; such an index is marked)."""
    cat = Catalog()
    locs = locations()
    assume = assume or {}
    warnings = []
    datasets = {}
    for slug, e in sorted(cat.entries.items()):
        listed = [name for name, prefix in locs["catalogues"].items() if probe(f"{prefix}{quote(slug)}/", pause)[0]]
        versions = []
        for v in e.versions():
            vid = v.get("version")
            files = []
            for f in v.get("files", []):
                if not isinstance(f, dict) or not f.get("path"):
                    continue
                rel = f"{slug}/{vid}/{f['path']}"
                found = []
                for name, prefix in locs["dumps"].items():
                    if name in assume:
                        p = Path(assume[name]) / rel
                        ok, size = p.is_file(), (p.stat().st_size if p.is_file() else None)
                    else:
                        ok, size = probe(prefix + quote(rel), pause)
                    if ok:
                        found.append(name)
                        if size is not None and f.get("bytes") is not None and size != f["bytes"]:
                            warnings.append(f"{name}: {rel} has {size} bytes, the catalogue {f['bytes']}")
                files.append({"path": f["path"], "bytes": f.get("bytes"), "sha256": f.get("sha256"),
                              "locations": found})
            if any(f["locations"] for f in files):
                versions.append({"version": vid, "issued": v.get("issued"), "status": e.status(vid),
                                 "files": files})
        if listed or versions:
            datasets[slug] = {"title": e.title, "stable": e.stable, "replaces": as_list(e.data.get("replaces")),
                              "replaced_by": cat.replaced_by(slug), "withdrawn": e.withdrawn, "catalogues": listed, "versions": versions}
        out(f"{slug}: catalogues {', '.join(listed) or '-'}; versions with files {len(versions)}")
    for w in warnings:
        out("warning: " + w)
    index = {"checked": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "locations": locs, "datasets": datasets}
    if assume:
        index["assumed"] = {k: "a local copy, not checked online (test)" for k in assume}
    return index


def write(index, path=INDEX):
    path.write_text(json.dumps(index, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def sync(site, index_path=INDEX, add=(), out=print):
    """Copy the entries the site has (and those in add) and the index into the Hugo site at `site`."""
    site = Path(site)
    content = site / "content" / "datasets"
    cat = Catalog()
    index = json.loads(Path(index_path).read_text(encoding="utf-8"))
    present = {p.stem for p in content.glob("*.md") if not p.name.startswith("_")}
    for slug in sorted(present | set(add)):
        e = cat.get(slug)
        if e is None:
            out(f"{slug}: in the site but not in the catalogue (left as it is)")
            continue
        text = e.path.read_text(encoding="utf-8")
        end = text.index("+++", 3) + 3
        new = text[:end] + "\n" + COPY_NOTE.format(slug=slug) + text[end:].lstrip("\n")
        target = content / f"{slug}.md"
        old = target.read_text(encoding="utf-8") if target.exists() else None
        if old != new:
            target.write_text(new, encoding="utf-8")
            out(f"{slug}: {'added' if old is None else 'updated'}")
        # the pictures of the entry (decision 0040), at /catalog/pictures/<slug>/ of the site
        pictures = CATALOG / "pictures" / slug
        if pictures.is_dir():
            dest = site / "static" / "catalog" / "pictures" / slug
            dest.mkdir(parents=True, exist_ok=True)
            for f in sorted(pictures.iterdir()):
                if f.is_file() and (not (dest / f.name).exists() or (dest / f.name).read_bytes() != f.read_bytes()):
                    shutil.copyfile(f, dest / f.name)
                    out(f"{slug}: picture {f.name}")
    missing = sorted(set(cat.entries) - present - set(add))
    if missing:
        out(f"not in the site (add with --add): {', '.join(missing)}")
    data = site / "data"
    data.mkdir(exist_ok=True)
    vocab = tomllib.loads((CATALOG / "vocabulary.toml").read_text(encoding="utf-8"))
    (data / "catalogvocabulary.json").write_text(json.dumps(vocab, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (data / "dataindex.json").write_text(json.dumps(index, ensure_ascii=False) + "\n", encoding="utf-8")
    out(f"data/dataindex.json: checked {index['checked']}" + (" (TEST: assumed locations)" if index.get("assumed") else ""))
