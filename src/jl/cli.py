"""The jl command line (decision 0018). Commands are verb-noun; the read commands take --json."""

import argparse
import json
import sys
from pathlib import Path

from . import canonical, catalog, config, generator, inputs, rdf, runs, versions
from .agents import AgentError, Registry, person_iri, software_iri

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
            info["local"] = str(local) if local.is_file() else None
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
    return out


def is_rdf(path):
    return isinstance(path, str) and rdf.rdf_format(path) is not None


def is_meta(path):
    return Path(path).name.split(".")[0].endswith("-meta")


def add_counts(cfg, files, count=False):
    """Fill in triple counts of RDF files from the canonical cache; count=True makes missing ones from the
    files in the store. Catalogue values are kept; a differing measurement is reported as 'measured'."""
    if not (cfg.path("cache") or cfg.build):
        return files
    for f in files:
        if not is_rdf(f["path"]) or not f.get("sha256"):
            continue
        info = canonical.cached_info(f["sha256"], cfg)
        if info is None and count and f.get("local"):
            info = canonical.canonical(f["local"], cfg)
            if info["sha256"] != f["sha256"]:
                f["store"] = "checksum differs"
                continue
        if info is None:
            continue
        f["canonical"] = info
        if f.get("triples") is None:
            f["triples"] = info["triples"]
        elif f["triples"] != info["triples"]:
            f["measured"] = info["triples"]
    return files


def total_triples(files, cfg=None, count=False):
    """Distinct triples of the graph of the version (all public RDF files without the -meta): the size of the
    union of their canonical forms, cached; None if not counted yet."""
    rdf_files = [f for f in files if f["public"] and is_rdf(f["path"]) and not is_meta(f["path"])]
    if not rdf_files:
        return None
    if len(rdf_files) == 1:
        return rdf_files[0].get("triples")
    if cfg is None or not all(f.get("canonical") for f in rdf_files):
        return None
    return canonical.union_count([f["canonical"] for f in rdf_files], cfg, make=count)


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
                       "stable_triples": total_triples(add_counts(cfg, version_files(cfg, e, stable)), cfg)
                       if stable else None,
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
        files = add_counts(cfg, version_files(cfg, e, v))
        rows.append({"version": v.get("version"), "status": e.status(v.get("version")), "issued": v.get("issued"),
                     "author": catalog.as_list(v.get("author")), "files": len(files),
                     "bytes": sum(f["bytes"] or 0 for f in files if f["public"]), "triples": total_triples(files, cfg),
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
    files = add_counts(cfg, version_files(cfg, e, v, verify=args.verify), count=args.count)
    rec = runs.version_record(slug, vid)
    obj = {"slug": slug, "version": vid, "status": e.status(vid),
           "iri": f"http://data.judaicalink.org/datasets/{slug}/{vid}",
           "fields": {k: val for k, val in v.items() if k != "files"}, "files": files,
           "triples": total_triples(files, cfg, count=args.count), "run_record": rec,
           "changelog": [c for c in e.changelog() if c.get("version") == vid]}

    def text(o):
        f = o["fields"]
        yield f"{o['slug']}/{o['version']} ({o['status']})  {o['iri']}"
        for k in ("issued", "author", "commit", "description", "withdrawn"):
            if k in f:
                val = f[k]
                yield f"  {k:<12} {', '.join(val) if isinstance(val, list) else val}"
        yield ""
        yield from ("  " + line for line in table(
            [[x["path"], f"{x['bytes']:,}" if isinstance(x["bytes"], int) else "–",
              (f"{x['triples']:,}" if isinstance(x["triples"], int) else ("–" if is_rdf(x["path"]) else ""))
              + (f" (measured {x['measured']:,})" if x.get("measured") is not None else ""),
              "public" if x["public"] else "store only", x["store"],
              (x["sha256"] or "–")[:12]] for x in o["files"]],
            ["file", "bytes", "triples", "", "in store", "sha256"]))
        t = o["triples"]
        yield f"  {len(o['files'])} files; triples in the graph (without -meta): " + (
            f"{t:,}" if t is not None else "not counted yet (show-version --count)")
        for x in o["files"]:
            c = x.get("canonical") or {}
            notes = [f"{c['statements'] - c['triples']:,} duplicate statements" if c.get("statements", 0) > c.get("triples", 0) else "",
                     f"{c['rdf_star']} RDF-star statement(s) left out" if c.get("rdf_star") else "",
                     f"{c['blank_node_triples']:,} triples with blank nodes" if c.get("blank_node_triples") else "",
                     f"tar archive ({', '.join(c['members'])})" if len(c.get("members", [])) > 1
                     or (c.get("members") and c["members"][0] != c.get("name")) else ""]
            if any(notes):
                yield f"  {x['path']}: " + "; ".join(n for n in notes if n)
        for x in o["files"]:
            if x["description"]:
                yield f"  {x['path']}: {x['description']}"
        yield ""
        if o["run_record"]:
            r = o["run_record"]
            yield f"  run record: generators/{o['slug']}/runs/{o['version']}.json" + (
                f" (run {r.get('run')}, commit {str(r.get('commit'))[:7]})" if r.get("run") else "")
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
    rows = [{"run": r["id"], "status": (r["record"] or {}).get("status", "?"),
             "version": runs.version_of_run(e.name, r["id"]),
             "uncommitted": bool((r["record"] or {}).get("uncommitted")),
             "files": len((r["record"] or {}).get("files", [])), "dir": str(r["dir"])} for r in found]

    def text(o):
        rows = o["runs"]
        if not cfg.build:
            yield "build area not configured (local.toml)"
            return
        if not rows:
            yield f"no runs of {e.name} in {cfg.build / e.name}"
            return
        yield from table([[r["run"], r["status"] + (" (uncommitted code)" if r["uncommitted"] else ""),
                           r["version"] or "–", r["files"]] for r in rows], ["run", "status", "version", "files"])
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
    reg = Registry()
    names = cat.names()
    persons = []
    for n, t in sorted(reg.persons.items()):
        persons.append({"number": n, "iri": person_iri(n), "name": t.get("name"), "withdrawn": t.get("withdrawn"),
                        "links": t.get("links", []), "datasets": names.get(t.get("name"), [])})
    software = [{"name": k, "iri": software_iri(k), **t} for k, t in sorted(reg.software.items())]
    registered = {p["name"] for p in persons}
    obj = {"persons": persons, "software": software, "errors": reg.errors,
           "unregistered": {n: s for n, s in names.items() if n not in registered}}

    def text(o):
        yield from table([[p["number"], p["name"] or f"(withdrawn: {p['withdrawn']})", len(p["datasets"]),
                           ", ".join(p["datasets"])] for p in o["persons"]], ["n", "person", "datasets", "slugs"])
        yield ""
        yield from table([[s["name"], s.get("label", "")] for s in o["software"]], ["software", "label"])
        for err in o["errors"]:
            yield f"error: {err}"
        for n, slugs in o["unregistered"].items():
            yield f"not registered: {n} ({', '.join(slugs)})"
    emit(args, obj, text)
    return 1 if obj["errors"] or obj["unregistered"] else 0


# --- generating: compare, show-canonical ---------------------------------------------------------

def resolve_files(cfg, ident):
    """The RDF files that an identifier names: [(name, path)], and a label.

    <slug>/<version> (the store), <slug>/<run-id> (the build area), <slug>/<version>/<path> (one file of a
    version), or a local file or directory."""
    p = Path(ident).expanduser()
    if p.exists():
        if p.is_file():
            return [(p.name, p)], str(p)
        return sorted((x.relative_to(p).as_posix(), x) for x in p.rglob("*") if x.is_file() and is_rdf(x.name)), str(p)
    slug, rest = split_id(ident)
    if not rest:
        raise LookupError(f"{ident}: not a file, and not <slug>/<version> or <slug>/<run-id>")
    head, _, path = rest.partition("/")
    if runs.is_run_id(head):
        r = runs.get_run(cfg.require("build"), slug, head)
        if r is None:
            raise LookupError(f"no run {slug}/{head} in {cfg.build}")
        files = sorted((x.relative_to(r["dir"]).as_posix(), x) for x in r["dir"].rglob("*")
                       if x.is_file() and is_rdf(x.name))
    else:
        e = load_entry(catalog.Catalog(), slug)
        v = e.version(head)
        if v is None:
            raise LookupError(f"{slug} has no version '{head}'")
        files = []
        for f in version_files(cfg, e, v):
            if not is_rdf(f["path"]):
                continue
            if not f.get("local"):
                raise LookupError(f"{slug}/{head}/{f['path']} is not in the store ({cfg.store})")
            files.append((f["path"], Path(f["local"])))
    if path:
        files = [(n, x) for n, x in files if n == path]
        if not files:
            raise LookupError(f"{ident}: no such RDF file")
    return files, ident


def select_part(files, meta):
    return [(n, p) for n, p in files if is_meta(n) == meta]


def cmd_generate(args, cfg):
    d, rec = generator.generate(cfg, args.slug, args.param, args.input)
    print(f"{args.slug}/{rec['run']}: {rec['status']}" + (f" ({rec['error']})" if rec.get("error") else "")
          + f", {rec['seconds']} s")
    print(f"  {d}")
    if rec["uncommitted"]:
        print(f"  uncommitted code: {', '.join(rec['uncommitted'])} (cannot become a version)")
    for f in rec["files"]:
        t = f" {f['triples']:>10,} triples" if "triples" in f else ""
        print(f"  {f['path']:<32} {f['bytes']:>12,} bytes{t}")
    for n in rec.get("notes", []):
        print(f"  note: {n}")
    if rec["status"] != "ok":
        print(f"  log: {d / 'log.txt'}")
        return 1
    e = catalog.Catalog().get(args.slug)
    if e and e.stable:
        print(f"  compare: ./jl compare {args.slug}/{e.stable} {args.slug}/{rec['run']}")
    return 0


def cmd_compare(args, cfg):
    fa, la = resolve_files(cfg, args.a)
    fb, lb = resolve_files(cfg, args.b)
    if not (len(fa) == len(fb) == 1 and Path(args.a).exists() and Path(args.b).exists()):
        fa, fb = select_part(fa, args.meta), select_part(fb, args.meta)
    part = "-meta file" if args.meta else "data file"
    ia = [canonical.canonical(p, cfg) for _, p in fa]
    ib = [canonical.canonical(p, cfg) for _, p in fb]
    write = None
    if args.write:
        args.write.mkdir(parents=True, exist_ok=True)
        write = (open(args.write / "only-a.nt", "w", encoding="utf-8"), open(args.write / "only-b.nt", "w", encoding="utf-8"))
    try:
        res = canonical.compare(canonical.union(ia), canonical.union(ib), examples=args.examples, write=write)
    finally:
        for f in write or ():
            f.close()
    per_file = []
    if args.per_file:
        common = sorted(set(n for n, _ in fa) & set(n for n, _ in fb))
        da, db = dict(zip((n for n, _ in fa), ia)), dict(zip((n for n, _ in fb), ib))
        for n in common:
            r = canonical.compare(canonical.lines(da[n]), canonical.lines(db[n]), examples=0)
            per_file.append({"file": n, **{k: r[k] for k in ("a", "b", "common", "only_a", "only_b", "identical")}})
    obj = {"a": {"label": la, "files": [n for n, _ in fa], "triples": res.pop("a")},
           "b": {"label": lb, "files": [n for n, _ in fb], "triples": res.pop("b")},
           "part": part, **res, "per_file": per_file}

    def text(o):
        for side in ("a", "b"):
            n = len(o[side]["files"])
            yield f"{side}: {o[side]['label']}: {n} {part}{'s' if n != 1 else ''}, {o[side]['triples']:,} triples"
        if o["identical"]:
            yield f"identical: the same {o['common']:,} triples"
        else:
            yield f"different: {o['common']:,} in both, {o['only_a']:,} only in a, {o['only_b']:,} only in b"
            for side in ("a", "b"):
                if o["examples_only_" + side]:
                    yield f"  only in {side}:"
                    yield from ("    " + x for x in o["examples_only_" + side])
        if o["per_file"]:
            yield ""
            yield from ("  " + line for line in table(
                [[r["file"], f"{r['a']:,}", f"{r['b']:,}", f"{r['only_a']:,}", f"{r['only_b']:,}",
                  "identical" if r["identical"] else ""] for r in o["per_file"]],
                ["file (in both)", "a", "b", "only a", "only b", ""]))
        if args.write:
            yield f"written: {args.write / 'only-a.nt'}, {args.write / 'only-b.nt'}"
    emit(args, obj, text)
    return 0 if obj["identical"] else 1


def cmd_show_canonical(args, cfg):
    files, label = resolve_files(cfg, args.id)
    if len(files) > 1 and not args.all:
        files = select_part(files, args.meta)
    infos = [canonical.canonical(p, cfg) for _, p in files]
    if args.count:
        n = canonical.union_count(infos, cfg, make=True) if len(infos) > 1 else infos[0]["triples"] if infos else 0
        print(f"{n:,} triples in {len(infos)} file(s) of {label}")
        for (name, _), i in zip(files, infos):
            print(f"  {i['triples']:>12,}  {name}" + (f"  ({i['statements'] - i['triples']:,} duplicates)"
                                                       if i["statements"] > i["triples"] else ""))
        return 0
    for line in canonical.union(infos):
        sys.stdout.write(line + "\n")
    return 0


# --- versions and metadata ------------------------------------------------------------------------

def cmd_add_version(args, cfg):
    slug, run_id = split_id(args.id)
    if not run_id or not runs.is_run_id(run_id):
        return fail("give <slug>/<run-id>")
    vid, d, v, warnings = versions.add_version(cfg, slug, run_id, version=args.version, author=args.author,
                                               description=args.description,
                                               text=args.text, issued=args.issued, dry_run=args.dry_run)
    print(f"{slug}/{vid}" + (" (dry run, nothing changed)" if args.dry_run else "") + f": {d}")
    for f in v["files"]:
        t = f" {f['triples']:>10,} triples" if f.get("triples") is not None else ""
        print(f"  {f['path']:<32} {f['bytes']:>12,} bytes{t}")
    for w in warnings:
        print(f"  warning: {w}")
    if args.dry_run:
        print(f"  entry as it would be: {d / 'catalog-entry.md'}; run record: {d / 'run.json'}")
    else:
        print(f"  catalogue entry, generators/{slug}/runs/{vid}.json: review and commit; stable is unchanged")
    return 0


def cmd_import_files(args, cfg):
    slug, vid = split_id(args.id)
    if vid:
        if args.files:
            return fail("give files only with <slug> (a new run), not with <slug>/<version>")
        rec = versions.import_version(cfg, slug, vid, args.description, origin=args.origin, sources=args.source,
                                      notes=args.note, dry_run=args.dry_run)
        print(f"{slug}/{vid}: run record (import)" + (" (dry run, not written)" if args.dry_run else
                                                      f": generators/{slug}/runs/{vid}.json"))
        for f in rec["files"]:
            t = f" {f['triples']:>10,} triples" if f.get("triples") is not None else ""
            print(f"  {f['path']:<32} {f['bytes']:>12,} bytes{t}")
        print(f"  then: ./jl render-meta {slug}/{vid}")
        return 0
    if not args.files:
        return fail("give the files to import (or <slug>/<version> to attach a record to a version)")
    d, rec = versions.import_files(cfg, slug, args.files, args.origin, args.description, sources=args.source,
                                   notes=args.note)
    print(f"{slug}/{rec['run']}: imported {len(rec['files'])} file(s): {d}")
    if rec["uncommitted"]:
        print(f"  uncommitted framework code: {', '.join(rec['uncommitted'])} (cannot become a version)")
    print(f"  then: ./jl add-version {slug}/{rec['run']} [--issued YYYY-MM-DD]")
    return 0


def cmd_remove_version(args, cfg):
    slug, vid = split_id(args.id)
    if not vid:
        return fail("give <slug>/<version>")
    if not args.unpublished:
        return fail("only a version that was never published can be removed; confirm with --unpublished")
    was_stable = versions.remove_version(cfg, slug, vid)
    print(f"{slug}/{vid} removed (catalogue, store, run record, run)" + ("; it was stable, stable is unset" if was_stable else ""))
    return 0


def cmd_add_input(args, cfg):
    root = cfg.require("inputs")
    texts = {"title": args.title, "origin": args.origin, "description": args.description, "date": args.date,
             "note": args.note}
    added = inputs.add(root, args.name, args.files, texts, move=args.move)
    print(f"inputs:{args.name}: {'moved' if args.move else 'copied'} {', '.join(added) or 'nothing'}; "
          f"described in {root / args.name / inputs.DESCRIPTION}")
    return 0


def cmd_check_inputs(args, cfg):
    root = cfg.require("inputs")
    res = inputs.check(root, verify=not args.quick)
    bad = 0
    for name, n, problems in res:
        print(f"inputs:{name}: {n} file{'s' if n != 1 else ''}" + (f", {len(problems)} problem(s)" if problems else ""))
        for pr in problems:
            print(f"  {pr}")
        bad += bool(problems)
    print(f"{len(res)} inputs, {bad} with problems", file=sys.stderr)
    return 1 if bad else 0


def cmd_clean_runs(args, cfg):
    gone = runs.clean(cfg.require("build"), args.slug, dry_run=args.dry_run)
    for d in gone:
        print(f"{'would delete' if args.dry_run else 'deleted'} {d.parent.name}/{d.name}")
    print(f"{len(gone)} run(s) {'to delete' if args.dry_run else 'deleted'}; runs of versions kept", file=sys.stderr)
    return 0


def cmd_render_meta(args, cfg):
    if args.all:
        if args.id or args.out:
            return fail("--all renders every version; give no <slug>/<version> and no --out")
        counts = versions.render_meta_all(cfg, dry_run=args.dry_run)
        print(", ".join(f"{n} {k}" for k, n in sorted(counts.items())), file=sys.stderr)
        return 0
    if not args.id:
        return fail("give <slug>/<version> or --all")
    slug, vid = split_id(args.id)
    if not vid:
        return fail("give <slug>/<version>")
    status, info = versions.render_meta(cfg, slug, vid, dry_run=args.dry_run, out=args.out)
    print(f"{slug}/{vid}: {status}" + (f" ({info['triples']} triples, {info['bytes']:,} bytes)" if info else ""))
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
        (("--verify",), {"action": "store_true", "help": "compare the checksums of the files in the store"}),
        (("--count",), {"action": "store_true", "help": "count the triples of files not counted yet (reads them)"}))
    add("list-runs", cmd_list_runs, "list the runs of a dataset in the build area", slug)
    add("show-run", cmd_show_run, "show a run: run record, outputs, log", (("id",), {"metavar": "<slug>/<run-id>"}))
    target = "<slug>/<version>, <slug>/<run-id>, <slug>/<version>/<path>, or a local file or directory"
    add("generate", cmd_generate, "run the generator of a dataset into the build area (a run, not a version)",
        slug,
        (("--param",), {"metavar": "K=V", "action": "append", "default": [], "help": "set a parameter; repeatable"}),
        (("--input",), {"metavar": "NAME=REF", "action": "append", "default": [],
                        "help": "use another input for a declared name (recorded); repeatable"}),
        json_out=False)
    add("compare", cmd_compare, "compare the triples of two versions, runs or files (exit 1 if they differ)",
        (("a",), {"metavar": "<a>", "help": target}), (("b",), {"metavar": "<b>"}),
        (("--meta",), {"action": "store_true", "help": "compare the -meta files instead of the data files"}),
        (("--per-file",), {"action": "store_true", "help": "also compare files with the same path"}),
        (("--examples",), {"type": int, "default": 5, "help": "lines shown of each side (default 5)"}),
        (("--write",), {"metavar": "DIR", "type": Path, "help": "write only-a.nt and only-b.nt to DIR"}))
    add("show-canonical", cmd_show_canonical, "print the canonical form (sorted, deduplicated N-Triples)",
        (("id",), {"metavar": "<what>", "help": target}),
        (("--meta",), {"action": "store_true", "help": "the -meta files instead of the data files"}),
        (("--all",), {"action": "store_true", "help": "data and -meta files together"}),
        (("--count",), {"action": "store_true", "help": "only count the triples"}), json_out=False)
    add("add-version", cmd_add_version, "make a run a version: header comments, -meta, run record, catalogue, store",
        (("id",), {"metavar": "<slug>/<run-id>"}),
        (("--version",), {"help": "the version id (default: the run date, -2, -3 … if taken)"}),
        (("--author",), {"help": "who makes the version (default: git config user.name); must be registered"}),
        (("--description",), {"help": "a short remark on the version (catalogue)"}),
        (("--text",), {"help": "the changelog text"}),
        (("--issued",), {"metavar": "YYYY-MM-DD", "help": "the date the data was made (default: the run date)"}),
        (("--dry-run",), {"action": "store_true",
                          "help": "write the version into the build area only; catalogue, store, run unchanged"}),
        json_out=False)
    add("import-files", cmd_import_files,
        "take files made elsewhere in as a run (<slug> files…), or attach a run record to a version (<slug>/<version>)",
        (("id",), {"metavar": "<slug>[/<version>]"}),
        (("files",), {"nargs": "*", "type": Path, "metavar": "FILE"}),
        (("--origin",), {"help": "where the files come from (a URL where there is one, else text)"}),
        (("--description",), {"help": "what the files are and how they were made"}),
        (("--source",), {"metavar": "URL", "action": "append", "default": [],
                         "help": "code or documentation that made the files (e.g. at a commit); repeatable"}),
        (("--note",), {"action": "append", "default": [], "help": "a remark for the run record; repeatable"}),
        (("--dry-run",), {"action": "store_true", "help": "<slug>/<version>: show the record, do not write it"}),
        json_out=False)
    add("remove-version", cmd_remove_version, "remove a version that was never published (catalogue, store, run record)",
        (("id",), {"metavar": "<slug>/<version>"}),
        (("--unpublished",), {"action": "store_true", "help": "confirm that no copy of it was ever published"}),
        json_out=False)
    add("render-meta", cmd_render_meta, "render the -meta of a version again (replaced only if its content changed)",
        (("id",), {"metavar": "<slug>/<version>", "nargs": "?"}),
        (("--all",), {"action": "store_true", "help": "every version of the catalogue"}),
        (("--dry-run",), {"action": "store_true", "help": "only say whether it would change"}),
        (("--out",), {"metavar": "FILE", "type": Path, "help": "write the -meta to FILE; nothing else changes"}),
        json_out=False)
    add("add-input", cmd_add_input, "put files into the inputs area and describe them (input.toml, decision 0021)",
        (("name",), {"metavar": "<source>/<name>"}),
        (("files",), {"nargs": "+", "type": Path, "metavar": "FILE_OR_DIR"}),
        (("--title",), {}), (("--origin",), {"help": "a URL where there is one, else text"}),
        (("--description",), {}), (("--date",), {"help": "when it was made or received (default: today)"}),
        (("--note",), {"help": "e.g. why it is not published"}),
        (("--move",), {"action": "store_true", "help": "move instead of copy"}), json_out=False)
    add("check-inputs", cmd_check_inputs, "check the inputs area: every file described, sizes and checksums",
        (("--quick",), {"action": "store_true", "help": "sizes only, no checksums"}), json_out=False)
    add("clean-runs", cmd_clean_runs, "delete the runs in the build area that did not become a version",
        (("slug",), {"nargs": "*", "help": "only these datasets (default: all)"}),
        (("--dry-run",), {"action": "store_true", "help": "only list them"}), json_out=False)
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
    except (LookupError, config.ConfigError, generator.GeneratorError, ValueError, OSError) as e:
        return fail(str(e))
    except BrokenPipeError:
        return 0
