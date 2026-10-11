"""The jl command line (decision 0018). Commands are verb-noun; the read commands take --json."""

import argparse
import json
import sys
from pathlib import Path

from . import catalog, config, runs

def emit(args, obj, text):
    """Print obj as JSON with --json, else the lines of text(obj)."""
    if getattr(args, "json", False):
        print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))
    else:
        for line in text(obj):
            print(line)


def table(rows, headers):
    """Lines of a plain text table."""
    rows = [[("" if c is None else str(c)) for c in r] for r in rows]
    widths = [max([len(h)] + [len(r[i]) for r in rows]) for i, h in enumerate(headers)]
    yield "  ".join(h.ljust(w) for h, w in zip(headers, widths)).rstrip()
    for r in rows:
        yield "  ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip()


def fail(msg):
    print(f"jl: {msg}", file=sys.stderr)
    return 2


def split_id(ident, what="dataset"):
    """'<slug>' or '<slug>/<version or run-id>' -> (slug, rest or None)."""
    slug, _, rest = ident.partition("/")
    return slug, (rest or None)


def load_entry(cat, slug):
    e = cat.get(slug)
    if e is None:
        raise LookupError(f"no dataset '{slug}' in the catalogue"
                          + (f" ({cat.errors[slug + '.md']})" if slug + ".md" in cat.errors else ""))
    return e


def version_files(cfg, e, v, verify=False):
    """The files of a version with what is known about them: catalogue values, the store, the run record."""
    rec = runs.version_record(e.name, v["version"]) or {}
    counted = {f.get("path"): f.get("triples") for f in rec.get("files", []) if isinstance(f, dict)}
    out = []
    for f in v.get("files", []):
        if not isinstance(f, dict):
            continue
        p = f.get("path")
        info = {"path": p, "bytes": f.get("bytes"), "sha256": f.get("sha256"),
                "triples": f.get("triples", counted.get(p)), "public": True,
                "description": e.file_description(p, v)}
        if cfg.store:
            local = cfg.store / e.name / v["version"] / p
            if not local.is_file():
                info["store"] = "missing"
            elif isinstance(f.get("bytes"), int) and local.stat().st_size != f["bytes"]:
                info["store"] = "size differs"
            elif verify and f.get("sha256") and catalog.sha256(local) != f["sha256"]:
                info["store"] = "checksum differs"
            else:
                info["store"] = "verified" if verify and f.get("sha256") else "present"
        else:
            info["store"] = "not configured"
        out.append(info)
    # files of the version that are only in the store (named by the run record, not published)
    listed = {i["path"] for i in out}
    for f in rec.get("files", []):
        if isinstance(f, dict) and f.get("path") not in listed:
            out.append({"path": f.get("path"), "bytes": f.get("bytes"), "sha256": f.get("sha256"),
                        "triples": f.get("triples"), "public": False, "description": f.get("description"),
                        "store": "named by the run record"})
    return out


RDF_SUFFIXES = (".ttl", ".ttl.gz", ".nt", ".nt.gz", ".n3", ".n3.gz", ".rdf", ".rdf.gz", ".owl", ".owl.gz")


def is_rdf(path):
    return isinstance(path, str) and path.endswith(RDF_SUFFIXES)


def total_triples(files):
    counts = [f["triples"] for f in files if f["public"] and is_rdf(f["path"])]
    if not counts:
        return None
    return sum(counts) if all(isinstance(c, int) for c in counts) else None


# --- read commands -------------------------------------------------------------------------------

def cmd_list_datasets(args, cfg):
    cat = catalog.Catalog()
    rows = []
    for s, e in sorted(cat.entries.items()):
        rows.append({"slug": s, "title": e.title, "kind": e.data.get("kind"), "stable": e.stable,
                     "versions": len(e.versions()), "replaced_by": cat.replaced_by(s),
                     "withdrawn": e.data.get("withdrawn")})

    def text(o):
        rows = o["datasets"]
        yield from table([[r["slug"], r["kind"] or "–", r["stable"] or "–", r["versions"],
                           ("replaced by " + ", ".join(r["replaced_by"]) if r["replaced_by"] else "")
                           + ("withdrawn" if r["withdrawn"] else ""), r["title"]] for r in rows],
                         ["slug", "kind", "stable", "versions", "notes", "title"])
        yield f"{len(rows)} datasets" + (f"; unreadable: {', '.join(cat.errors)}" if cat.errors else "")
    emit(args, {"datasets": rows, "unreadable": cat.errors}, text)
    return 0


def cmd_show_dataset(args, cfg):
    cat = catalog.Catalog()
    e = load_entry(cat, args.slug)
    stable = e.version(e.stable) if e.stable else None
    obj = {"slug": e.name, "fields": e.data, "summary": e.summary(),
           "derived": {"stable": e.stable,
                       "stable_triples": total_triples(version_files(cfg, e, stable)) if stable else None,
                       "versions": [(v.get("version"), e.status(v.get("version"))) for v in e.versions()],
                       "contributors": e.contributors(), "replaced_by": cat.replaced_by(e.name),
                       "used_by": cat.used_by(e.name), "generator": catalog.generator_folder(e.name),
                       "graph": f"http://data.judaicalink.org/datasets/{e.name}",
                       "metadata_graph": f"http://data.judaicalink.org/datasets/{e.name}/meta"}}

    def text(o):
        d, x = o["fields"], o["derived"]
        yield f"{o['slug']}: {d.get('title', '')}"
        yield ""
        for k in ("author", "kind", "method", "namespaces", "website", "example", "date", "inputs", "replaces",
                  "aliases", "withdrawn"):
            if k in d:
                v = d[k]
                yield f"  {k:<12} {', '.join(map(str, v)) if isinstance(v, list) else v}"
        lic = d.get("license", {})
        yield f"  {'license':<12} {lic.get('name', '')} {lic.get('uri', '')}".rstrip()
        for link in d.get("links", []):
            yield f"  {'link':<12} {link.get('url')}  {link.get('label', '')}".rstrip()
        yield ""
        yield f"  {'graph':<12} {x['graph']}"
        yield f"  {'meta graph':<12} {x['metadata_graph']}"
        yield f"  {'stable':<12} {x['stable'] or '– (all versions are previews)'}" + (
            f", {x['stable_triples']:,} triples" if x["stable_triples"] is not None else
            (", triples not counted" if x["stable"] else ""))
        for vid, status in x["versions"]:
            yield f"  {'version':<12} {vid} ({status})"
        yield f"  {'contributors':<12} {', '.join(x['contributors']) or '–'}"
        if x["replaced_by"]:
            yield f"  {'replaced by':<12} {', '.join(x['replaced_by'])}"
        if x["used_by"]:
            yield f"  {'used by':<12} {', '.join(x['used_by'])}"
        g = x["generator"]
        parts = [n for n, ok in (("README", g["readme"]), ("original/", g["original"]), ("generate.py", g["generate"]))
                 if ok]
        yield f"  {'generator':<12} generators/{o['slug']}/: " + (", ".join(parts) if g["folder"] else "no folder") + (
            f"; run records: {', '.join(g['run_records'])}" if g["run_records"] else "")
        changes = d.get("changelog", [])
        if changes:
            yield ""
            yield "  changelog:"
            for c in changes:
                who = ", ".join(catalog.as_list(c.get("author"))) or "–"
                yield f"    {c.get('date')}  {who}{'  [' + c['version'] + ']' if c.get('version') else ''}: {c.get('text', '')}"
        if o["summary"]:
            yield ""
            yield "  " + o["summary"]
    emit(args, obj, text)
    return 0


def cmd_list_versions(args, cfg):
    cat = catalog.Catalog()
    e = load_entry(cat, args.slug)
    rows = []
    for v in e.versions():
        files = version_files(cfg, e, v)
        rows.append({"version": v.get("version"), "status": e.status(v.get("version")), "issued": v.get("issued"),
                     "author": catalog.as_list(v.get("author")), "files": len(files),
                     "bytes": sum(f["bytes"] or 0 for f in files if f["public"]), "triples": total_triples(files),
                     "store": sorted({f["store"] for f in files}), "description": v.get("description")})

    def text(o):
        rows = o["versions"]
        yield from table([[r["version"], r["status"], r["issued"], ", ".join(r["author"]) or "–", r["files"],
                           f"{r['bytes']:,}", f"{r['triples']:,}" if r["triples"] is not None else "–",
                           ", ".join(r["store"])] for r in rows],
                         ["version", "status", "issued", "author", "files", "bytes", "triples", "store"])
    emit(args, {"slug": e.name, "versions": rows}, text)
    return 0


def cmd_show_version(args, cfg):
    cat = catalog.Catalog()
    slug, vid = split_id(args.id)
    e = load_entry(cat, slug)
    if vid is None:
        raise LookupError("give a version: <slug>/<version>")
    if runs.is_run_id(vid):
        raise LookupError(f"{vid} is a run; use show-run")
    v = e.version(vid)
    if v is None:
        raise LookupError(f"{slug} has no version '{vid}' (versions: {', '.join(x.get('version') for x in e.versions())})")
    files = version_files(cfg, e, v, verify=args.verify)
    rec = runs.version_record(slug, vid)
    obj = {"slug": slug, "version": vid, "status": e.status(vid),
           "iri": f"http://data.judaicalink.org/datasets/{slug}/{vid}",
           "fields": {k: val for k, val in v.items() if k != "files"}, "files": files,
           "triples": total_triples(files), "run_record": rec,
           "changelog": [c for c in e.changelog() if c.get("version") == vid]}

    def text(o):
        f = o["fields"]
        yield f"{o['slug']}/{o['version']} ({o['status']})  {o['iri']}"
        for k in ("issued", "author", "commit", "graph", "description", "withdrawn"):
            if k in f:
                val = f[k]
                yield f"  {k:<12} {', '.join(val) if isinstance(val, list) else val}"
        yield ""
        yield from ("  " + line for line in table(
            [[x["path"], f"{x['bytes']:,}" if isinstance(x["bytes"], int) else "–",
              f"{x['triples']:,}" if isinstance(x["triples"], int) else ("–" if is_rdf(x["path"]) else ""),
              "public" if x["public"] else "store only", x["store"],
              (x["sha256"] or "–")[:12]] for x in o["files"]],
            ["file", "bytes", "triples", "", "in store", "sha256"]))
        t = o["triples"]
        yield f"  {len(o['files'])} files; triples: " + (f"{t:,}" if t is not None else
                                                         "not counted yet (needs the index service)")
        for x in o["files"]:
            if x["description"]:
                yield f"  {x['path']}: {x['description']}"
        yield ""
        if o["run_record"]:
            r = o["run_record"]
            yield f"  run record: generators/{o['slug']}/runs/{o['version']}.json" + (
                f" (run {r.get('run')}, {r.get('mode', '')})" if r.get("run") else "")
        else:
            yield "  run record: none yet"
        for c in o["changelog"]:
            yield f"  changelog {c.get('date')}: {c.get('text')}"
    emit(args, obj, text)
    return 0


def cmd_list_runs(args, cfg):
    cat = catalog.Catalog()
    e = load_entry(cat, args.slug)
    found = runs.list_runs(cfg.build, e.name)
    rows = [{"run": r["id"], "version": runs.version_of_run(e.name, r["id"]),
             "files": len((r["record"] or {}).get("files", [])), "dir": str(r["dir"])} for r in found]

    def text(o):
        rows = o["runs"]
        if not cfg.build:
            yield "build area not configured (local.toml)"
            return
        if not rows:
            yield f"no runs of {e.name} in {cfg.build / e.name}"
            return
        yield from table([[r["run"], r["version"] or "–", r["files"]] for r in rows], ["run", "version", "files"])
    emit(args, {"slug": e.name, "runs": rows}, text)
    return 0


def cmd_show_run(args, cfg):
    slug, rid = split_id(args.id)
    if not rid or not runs.is_run_id(rid):
        raise LookupError("give a run: <slug>/run-<YYYYMMDDTHHMMSSZ>")
    r = runs.get_run(cfg.require("build"), slug, rid)
    if r is None:
        raise LookupError(f"no run {slug}/{rid} in {cfg.build}")
    outputs = sorted(p.relative_to(r["dir"]).as_posix() for p in r["dir"].rglob("*")
                     if p.is_file() and p.name not in ("run.json", "log.txt"))
    obj = {"slug": slug, "run": rid, "dir": str(r["dir"]), "record": r["record"], "outputs": outputs,
           "version": runs.version_of_run(slug, rid), "log_tail": runs.log_tail(r)}

    def text(o):
        yield f"{o['slug']}/{o['run']}" + (f" (became version {o['version']})" if o["version"] else " (not a version)")
        yield f"  {o['dir']}"
        yield ""
        yield from ("  " + line for line in json.dumps(o["record"], indent=2, ensure_ascii=False,
                                                       default=str).splitlines())
        yield ""
        yield "  outputs: " + (", ".join(o["outputs"]) or "–")
        if o["log_tail"]:
            yield "  log:"
            yield from ("    " + line for line in o["log_tail"])
    emit(args, obj, text)
    return 0


def cmd_list_agents(args, cfg):
    cat = catalog.Catalog()
    registry = config.CATALOG / "agents.toml"
    names = cat.names()
    obj = {"registry": registry.is_file(), "names": names}

    def text(o):
        if not o["registry"]:
            yield "no registry yet (catalog/agents.toml, decision 0018); names in the catalogue:"
        yield from table([[n, len(slugs), ", ".join(slugs)] for n, slugs in o["names"].items()],
                         ["name", "datasets", "slugs"])
    emit(args, obj, text)
    return 0


# --- catalogue and store -------------------------------------------------------------------------

def cmd_check_catalog(args, cfg):
    dumps = list(args.dumps)
    if args.store:
        dumps.append(cfg.require("store"))
    n, errors, warnings = catalog.check(dumps=dumps, complete=args.complete)
    print(f"{n} entries, {errors} errors, {warnings} warnings", file=sys.stderr)
    return 1 if errors else 0


def cmd_collect_store(args, cfg):
    sources = list(args.sources) or cfg.paths("legacy_dumps")
    if not sources:
        return fail("no source directories (--from, or legacy_dumps in local.toml)")
    to = args.to or cfg.require("store")
    wanted, present, linked, missing = catalog.collect(sources, to, dry_run=args.dry_run)
    verb = "to link" if args.dry_run else "linked"
    print(f"{wanted} files: {present} in place, {linked} {verb}, {missing} missing or different", file=sys.stderr)
    return 1 if missing else 0


# --- parser --------------------------------------------------------------------------------------

def parser():
    ap = argparse.ArgumentParser(prog="jl", description="The generator framework of judaicalink-data (decision 0018).")
    sub = ap.add_subparsers(dest="command", required=True, metavar="<command>")

    def add(name, func, help, *arguments, json_out=True):
        p = sub.add_parser(name, help=help, description=help)
        for a, kw in arguments:
            p.add_argument(*a, **kw)
        if json_out:
            p.add_argument("--json", action="store_true", help="the parsed structure as JSON")
        p.set_defaults(func=func)
        return p

    slug = (("slug",), {"help": "dataset slug"})
    add("list-datasets", cmd_list_datasets, "list the datasets of the catalogue")
    add("show-dataset", cmd_show_dataset, "show a catalogue entry with the derived values", slug)
    add("list-versions", cmd_list_versions, "list the versions of a dataset", slug)
    add("show-version", cmd_show_version, "show a version: files, sizes, checksums, triples, store, run record",
        (("id",), {"metavar": "<slug>/<version>"}),
        (("--verify",), {"action": "store_true", "help": "compare the checksums of the files in the store"}))
    add("list-runs", cmd_list_runs, "list the runs of a dataset in the build area", slug)
    add("show-run", cmd_show_run, "show a run: run record, outputs, log", (("id",), {"metavar": "<slug>/<run-id>"}))
    add("list-agents", cmd_list_agents, "list the agents (registry) and the names used in the catalogue")
    add("check-catalog", cmd_check_catalog, "check the catalogue entries (0013, 0018) and local copies of the files",
        (("--store",), {"action": "store_true", "help": "also compare with the store (local.toml)"}),
        (("--dumps",), {"metavar": "DIR", "type": Path, "action": "append", "default": [],
                        "help": "another tree <slug>/<version>/<path> to compare with; repeatable"}),
        (("--complete",), {"action": "store_true",
                           "help": "each tree must hold exactly the catalogued files (no file missing, none extra)"}),
        json_out=False)
    add("collect-store", cmd_collect_store, "build the store <slug>/<version>/<path> from older trees by checksum",
        (("--from",), {"dest": "sources", "metavar": "DIR", "type": Path, "action": "append", "default": [],
                       "help": "directory to take files from (any layout); default: legacy_dumps of local.toml"}),
        (("--to",), {"metavar": "DIR", "type": Path, "help": "the tree to build (default: the store)"}),
        (("--dry-run",), {"action": "store_true", "help": "only report what would be linked"}),
        json_out=False)
    return ap


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        cfg = config.load()
        return args.func(args, cfg)
    except (LookupError, config.ConfigError) as e:
        return fail(str(e))
    except BrokenPipeError:
        return 0
