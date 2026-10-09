#!/usr/bin/env python3
"""One-off migration of the 36 old catalogue entries to the entry format of decision 0013.

Ran once on 2026-10-09 (catalog/README.md, section Migration); it reads only the old format, so it
cannot be run again on the migrated entries.

    python3 catalog/migrate_0013.py --dumps ../lokal/dumps [--out DIR]

Reads catalog/*.md (old format, catalog/README.md), writes the new entries to DIR (default: catalog/,
in place). --dumps is the local copy of the archive in its old structure (the paths behind
https://archive.judaicalink.org/dumps/); sizes and checksums of the files are taken from there.
Descriptions of files that only repeat the title, the body or each other are dropped and listed on stderr for review. Standard library only.
"""

import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import catalog  # noqa: E402

VERSION = "2026-09-26"
VERSION_DESCRIPTION = "Archived state, identical to the catalogue state judaicalink-site 81b42a5."
MIGRATED = "2026-10-09"
CHANGE = ("Migrated to the entry format of decision 0013: one version 2026-09-26 with the files of the "
          "archived catalogue state (judaicalink-site 81b42a5).")
DATASETS = "http://data.judaicalink.org/datasets/"
WITHDRAWN = {"cmtest": "A test index (Elasticsearch JSON) of a Compact Memory sample, not a dataset."}
GENERIC = re.compile(r"^(RDF dump of|Metadata for) (the )?\S+ dataset\.?$", re.I)


def clean(v):
    """Strip strings, drop empty strings and lists (returns None for empty)."""
    if isinstance(v, str):
        return v.strip() or None
    if isinstance(v, list):
        return v or None
    return v


def day(v):
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()[:10]
    return str(v).strip()[:10]


def file_path(url):
    """Path relative to <slug>/<version>/: the old path without the dump directory and 'current/'."""
    parts = url.split("/dumps/", 1)[1].split("/")[1:]
    if parts[0] == "current":
        parts = parts[1:]
    return "/".join(parts)


def norm(text):
    return re.sub(r"\W+", " ", text).strip().lower()


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def slug_of(url):
    """Slug from a catalogue page URL https://web.judaicalink.org/datasets/<slug>."""
    return url.rstrip("/").rsplit("/", 1)[1]


def migrate(e, dumps, dropped):
    old = {k: clean(v) for k, v in e.data.items()}
    old = {k: v for k, v in old.items() if v is not None}
    slug, title = e.name, old["title"]
    new = {"slug": slug, "title": title, "author": old["author"]}
    for k in ("authorlink",):
        if k in old:
            new[k] = old[k]
    new["date"] = day(old["date"])
    for k in ("website", "example", "picture"):
        if k in old:
            new[k] = old[k]
    if old.get("category") == "support":
        new["kind"] = "support"
    namespaces = ([old["dataslug"]] if "dataslug" in old else []) + old.get("namespace_slugs", [])
    if namespaces:
        new["namespaces"] = list(dict.fromkeys(namespaces))
    if "supportdata" in old:  # the main dataset is generated from its support data
        new["inputs"] = [slug_of(old["supportdata"])]
    if "aliases" in old:
        new["aliases"] = old["aliases"]

    files = old.get("files", [])
    if files:
        new["stable"] = VERSION
    if slug in WITHDRAWN:
        new["withdrawn"] = WITHDRAWN[slug]
        new.pop("stable", None)

    lic = {k: clean(v) for k, v in old["license"].items()}
    new["license"] = {k: lic[k] for k in ("name", "uri", "image") if lic.get(k)}

    gen = old.get("generator")
    m = re.match(r"^(https://github\.com/[^/]+/[^/]+)/blob/[^/]+/(.+)$", gen["gitweb"]) if gen else None
    if m:
        new["generator"] = {"repo": m.group(1), "path": m.group(2)}
    if "script" in old:
        new["links"] = [{"url": old["script"], "label": "Generator script"}]

    # versions and file descriptions
    paths = [file_path(f["url"]) for f in files]
    assert len(set(paths)) == len(paths), f"{slug}: duplicate paths {paths}"
    texts = [clean(f.get("description")) for f in files]
    descriptions = {}
    vfiles = []
    for f, path, text in zip(files, paths, texts):
        vf = {"path": path}
        local = dumps / f["url"].split("/dumps/", 1)[1]
        if local.is_file():
            vf["bytes"] = local.stat().st_size
            vf["sha256"] = sha256(local)
        vfiles.append(vf)
        if not text or text == "None":
            continue
        if (texts.count(text) > 1 or GENERIC.match(text) or norm(text) == norm(title)
                or norm(text) in norm(e.body)):
            dropped.append(f"{slug}: {path}: {text}")
        else:
            descriptions[path] = text
    if descriptions:
        new["files"] = descriptions
    if vfiles:
        v = {"version": VERSION, "issued": new["date"]}
        creators = old.get("creators")
        v["author"] = ", ".join(c["name"] for c in creators) if creators else old["author"]
        if not creators and "authorlink" in old:
            v["authorlink"] = old["authorlink"]
        elif creators and len(creators) == 1 and creators[0].get("url"):
            v["authorlink"] = creators[0]["url"]
        if gen and gen.get("commit"):
            v["commit"] = gen["commit"]
        if "graph" in old and old["graph"] != DATASETS + slug:
            v["graph"] = old["graph"]
        v["description"] = VERSION_DESCRIPTION
        v["files"] = vfiles
        new["versions"] = [v]
    new["changelog"] = [{"date": MIGRATED, "text": CHANGE, "refs": ["0013"]}]

    # body: the old free-text counts are kept as text
    body = e.body.rstrip("\n")
    counts = [f"{k}: {old[k]}" for k in ("concepts", "persons", "links") if isinstance(old.get(k), str)]
    if counts:
        body += "\n\nCounts in the former catalogue entry: " + "; ".join(counts) + "."
    return new, body + "\n"


# --- writing TOML --------------------------------------------------------------------------------

def value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return "[" + ", ".join(value(x) for x in v) + "]"
    raise TypeError(v)


def pairs(d, indent=""):
    return [f"{indent}{k} = {value(v)}" for k, v in d.items() if not isinstance(v, (dict, list))
            or (isinstance(v, list) and not any(isinstance(x, dict) for x in v))]


def to_toml(new):
    out = pairs(new)
    for k in ("license", "generator"):
        if k in new:
            out += ["", f"[{k}]"] + pairs(new[k])
    for link in new.get("links", []):
        out += ["", "[[links]]"] + pairs(link)
    if "files" in new:
        out += ["", "[files]"] + [f"{value(p)} = {value(t)}" for p, t in new["files"].items()]
    for v in new.get("versions", []):
        out += ["", "[[versions]]"] + pairs(v)
        for f in v["files"]:
            out += ["", "  [[versions.files]]"] + pairs(f, "  ")
    for c in new.get("changelog", []):
        out += ["", "[[changelog]]"] + pairs(c)
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dumps", type=Path, required=True, help="local archive in the old structure")
    ap.add_argument("--out", type=Path, default=catalog.CATALOG, help="output directory (default: catalog/)")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    dropped = []
    for path in catalog.entry_files():
        e = catalog.read_entry(path)
        new, body = migrate(e, args.dumps, dropped)
        (args.out / path.name).write_text("+++\n" + to_toml(new) + "+++\n" + body, encoding="utf-8")
    print("Dropped file descriptions:", *dropped, sep="\n  ", file=sys.stderr)


if __name__ == "__main__":
    main()
