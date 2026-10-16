"""Rendering the -meta file of a version (decision 0018).

The -meta is rendered from the catalogue entry, the run record of the version and statistics measured on its
files; generators never write it. It describes the dataset and the version, but no catalogue state that moves
(stable, replaced_by, the maintainer, contributors): moving the stable pointer rewrites no -meta. It names no
dumps location (0014) and names persons only by IRI (agents registry).

Two parts: the content, and the provenance of the metadata itself (all triples about the rendering activity:
time, framework commit). A -meta file is only rewritten when its content changed.
"""

import gzip
import re

from . import canonical, vocabulary
from .agents import software_iri
from .rdf import RDF_TYPE, XSD, IRI, Literal, nt_line, read_triples
from .turtle import PREFIXES, Namespace

JL = "http://data.judaicalink.org/"
REPO = "https://github.com/judaicalink/judaicalink-data"
LANDING_PAGE = "https://judaicalink.org/"
FINDER = "https://web.judaicalink.org/dataindex/?file="
MEDIA = "http://www.iana.org/assignments/media-types/"
SPDX = "http://spdx.org/rdf/terms#"
FRAMEWORK = "judaicalink-data"

CC, DCAT, DCTERMS, PROV, RDFS, VOID = (Namespace(PREFIXES[p]) for p in ("cc", "dcat", "dcterms", "prov", "rdfs", "void"))
SPDXNS = Namespace(SPDX)
A = IRI(RDF_TYPE)

MEDIA_TYPES = [(".ttl", "text/turtle"), (".nt", "application/n-triples"), (".n3", "text/n3"),
               (".rdf", "application/rdf+xml"), (".owl", "application/rdf+xml"),
               (".json", "application/json"), (".csv", "text/csv"), (".tsv", "text/tab-separated-values"),
               (".xml", "application/xml"), (".txt", "text/plain"), (".ru", "application/sparql-update")]


def dataset_iri(slug):
    return IRI(f"{JL}datasets/{slug}")


def version_iri(slug, version):
    return IRI(f"{JL}datasets/{slug}/{version}")


def file_iri(slug, version, path):
    return IRI(f"{JL}dumps/{slug}/{version}/{path}")


def meta_graph(slug):
    return IRI(f"{JL}datasets/{slug}/meta")


def meta_path(slug):
    return f"{slug}-meta.ttl.gz"


def header(slug, version, meta=False):
    """The header comments of a file of a version (0018)."""
    return [f"JudaicaLink dataset {slug}, version {version}" + (": metadata" if meta else ""),
            f"{version_iri(slug, version)}" + (f" (graph {meta_graph(slug)})" if meta else "")]


def is_url(s):
    return isinstance(s, str) and re.match(r"^https?://\S+$", s) is not None


def date(v):
    return Literal(str(v)[:10], XSD + "date")


def datetime(v):
    return Literal(str(v), XSD + "dateTime")


def integer(n):
    return Literal(str(n), XSD + "integer")


def media_type(path):
    name = path[:-3] if path.endswith(".gz") else path
    for ext, mt in MEDIA_TYPES:
        if name.endswith(ext):
            return IRI(MEDIA + mt)
    return None


# predicates that say a subject is no longer current: replaced, merged, split, retired or deprecated (0022, 0029)
NOT_CURRENT = {f"<{x}>" for x in (PREFIXES["dcterms"] + "isReplacedBy", PREFIXES["jl"] + "mergedInto",
                                  PREFIXES["jl"] + "splitInto", PREFIXES["jl"] + "retiredDate",
                                  PREFIXES["owl"] + "deprecated")}


def statistics(infos):
    """Measured on the canonical form of the data files (union): triples, distinct subjects, the distinct subjects
    that are current (not replaced, merged, split, retired or deprecated: the number of entities, which does not grow
    with every new IRI), properties, classes (objects of rdf:type), and the namespaces of the properties and classes
    (void:vocabulary)."""
    triples = subjects = gone = 0
    last, last_gone = None, False
    properties, classes = set(), set()
    type_iri = f"<{RDF_TYPE}>"
    for line in canonical.union(infos):
        triples += 1
        s, p, rest = line.split(" ", 2)
        if s != last:
            subjects += 1
            gone += last_gone
            last, last_gone = s, False
        if p in NOT_CURRENT:
            last_gone = True
        properties.add(p)
        if p == type_iri:
            classes.add(rest[:-2])
    gone += last_gone
    return {"triples": triples, "distinct_subjects": subjects, "current_subjects": subjects - gone,
            "properties": len(properties), "classes": len(classes),
            "vocabularies": sorted({namespace(t[1:-1]) for t in properties | classes} - {None})}


def namespace(term):
    """The namespace of a term: its IRI up to the last '#' or '/' (void:vocabulary)."""
    m = re.match(r"^(.*[#/])[^#/]+$", term)
    return m.group(1) if m else None


def commit_url(commit, path):
    return IRI(f"{REPO}/blob/{commit}/{path}")


def render(entry, version, files, record, stats, registry):
    """The content triples of the -meta of a version.

    entry: catalog.Entry; version: its version table; files: the public files of the version
    [{path, bytes, sha256, triples, description}] (without the -meta itself); record: the run record or None;
    stats: statistics() of the data files or None."""
    slug, vid = entry.name, version["version"]
    D, V = dataset_iri(slug), version_iri(slug, vid)
    t = []

    # the dataset
    d = entry.data
    t += [(D, A, DCAT.Dataset), (D, A, VOID.Dataset),
          (D, DCTERMS.identifier, Literal(slug)),
          (D, DCTERMS["title"], Literal(entry.title)),
          (D, DCAT.landingPage, IRI(LANDING_PAGE)),
          (D, DCAT.hasVersion, V)]
    if entry.summary():
        t.append((D, DCTERMS.abstract, Literal(entry.summary())))
    if entry.description():
        t.append((D, DCTERMS.description, Literal(entry.description())))
    for field in vocabulary.FIELDS:
        v = d.get(field)
        for x in [v] if isinstance(v, str) else v if isinstance(v, list) else []:
            t.append((D, DCTERMS.type, IRI(vocabulary.value_iri(field, x))))
    if set(d.get("method") or []) & vocabulary.automated():   # derived flag (0018)
        t.append((D, DCTERMS.type, IRI(vocabulary.value_iri("method", vocabulary.AUTOMATED))))
    lic = d.get("license") or {}
    if is_url(lic.get("uri")):
        t.append((D, DCTERMS.license, IRI(lic["uri"])))
    if lic.get("attribution"):   # the credit the licence asks for (0013)
        t.append((D, CC.attributionName, Literal(lic["attribution"])))
    if is_url(lic.get("statement")):   # where the source states the licence (0013)
        t.append((D, DCTERMS.rights, IRI(lic["statement"])))
    if is_url(d.get("website")):
        t.append((D, DCTERMS.source, IRI(d["website"])))
    if is_url(d.get("example")):
        t.append((D, VOID.exampleResource, IRI(d["example"])))
    for ns in d.get("namespaces", []) if isinstance(d.get("namespaces"), list) else []:
        t.append((D, VOID.uriSpace, Literal(f"{JL}data/{ns}/")))
    for r in d.get("replaces", []) if isinstance(d.get("replaces"), list) else []:
        t.append((D, DCTERMS.replaces, dataset_iri(r)))

    # the version
    t += [(V, A, DCAT.Dataset), (V, A, VOID.Dataset), (V, A, PROV.Entity),
          (V, DCAT.isVersionOf, D),
          (V, DCAT.version, Literal(vid))]
    if version.get("issued"):
        t.append((V, DCTERMS.issued, date(version["issued"])))
    if version.get("description"):
        t.append((V, DCTERMS.description, Literal(version["description"])))
    for name in [version["author"]] if isinstance(version.get("author"), str) else version.get("author", []):
        t.append((V, DCTERMS.creator, IRI(registry.person(name))))
    if version.get("withdrawn"):
        t.append((V, IRI(PREFIXES["owl"] + "deprecated"), Literal("true", XSD + "boolean")))
    if stats:
        t += [(V, VOID.triples, integer(stats["triples"])),
              (V, VOID.distinctSubjects, integer(stats["distinct_subjects"])),
              *([(V, IRI(PREFIXES["jl"] + "currentSubjects"), integer(stats["current_subjects"]))]
                if "current_subjects" in stats else []),
              (V, VOID.properties, integer(stats["properties"])),
              (V, VOID.classes, integer(stats["classes"]))]
        t += [(V, VOID.vocabulary, IRI(ns)) for ns in stats.get("vocabularies", [])]

    # the files
    for f in files + [{"path": meta_path(slug), "description": "Metadata of this version (this file)."}]:
        F = file_iri(slug, vid, f["path"])
        t += [(V, DCAT.distribution, F), (F, A, DCAT.Distribution),
              (F, DCAT.accessURL, IRI(FINDER + f"{slug}/{vid}/{f['path']}"))]
        desc = f.get("description") or entry.file_description(f["path"], version)
        if desc:
            t.append((F, DCTERMS.description, Literal(desc)))
        mt = media_type(f["path"])
        if mt:
            t.append((F, DCAT.mediaType, mt))
        if f["path"].endswith(".gz"):
            t.append((F, DCAT.compressFormat, IRI(MEDIA + "application/gzip")))
        if isinstance(f.get("bytes"), int):
            t.append((F, DCAT.byteSize, Literal(str(f["bytes"]), XSD + "nonNegativeInteger")))
        if f.get("sha256"):
            C = IRI(F + "#sha256")
            t += [(F, SPDXNS.checksum, C), (C, A, SPDXNS.Checksum),
                  (C, SPDXNS.algorithm, SPDXNS.checksumAlgorithm_sha256),
                  (C, SPDXNS.checksumValue, Literal(f["sha256"], XSD + "hexBinary"))]
        if isinstance(f.get("triples"), int):
            t.append((F, VOID.triples, integer(f["triples"])))

    # how the version was made (the run record)
    if record and record.get("mode") == "import":
        # made outside the framework: what is known, as text and links (the evidence is in the generator README)
        G = IRI(f"{V}/generation")
        t += [(V, PROV.wasGeneratedBy, G), (G, A, PROV.Activity),
              (G, RDFS.comment, Literal(record["description"])),
              (G, RDFS.seeAlso, IRI(f"{REPO}/blob/main/generators/{slug}/runs/{vid}.json"))]
        for name in [version["author"]] if isinstance(version.get("author"), str) else version.get("author", []):
            t.append((G, PROV.wasAssociatedWith, IRI(registry.person(name))))
        if record.get("origin"):
            t.append((G, RDFS.comment, Literal("Origin: " + record["origin"])))
        for note in record.get("notes", []):
            t.append((G, RDFS.comment, Literal(note)))
        for u in record.get("sources", []):
            if is_url(u):
                t.append((G, RDFS.seeAlso, IRI(u)))
    elif record and record.get("commit"):
        G = IRI(f"{V}/generation")
        commit = record["commit"]
        t += [(V, PROV.wasGeneratedBy, G), (G, A, PROV.Activity),
              (G, PROV.wasAssociatedWith, IRI(software_iri(FRAMEWORK))),
              (G, PROV.used, commit_url(commit, record.get("generator", f"generators/{slug}/generate.py"))),
              *[(G, PROV.used, commit_url(commit, path)) for path in record.get("shared_code", [])],
              (G, RDFS.seeAlso, IRI(f"{REPO}/blob/main/generators/{slug}/runs/{vid}.json"))]
        for name in [version["author"]] if isinstance(version.get("author"), str) else version.get("author", []):
            t.append((G, PROV.wasAssociatedWith, IRI(registry.person(name))))
        if record.get("started"):
            t.append((G, PROV.startedAtTime, datetime(record["started"])))
        if record.get("finished"):
            t.append((G, PROV.endedAtTime, datetime(record["finished"])))
        if record.get("params"):
            t.append((G, RDFS.comment, Literal("Parameters: " + ", ".join(
                f"{k} = {v!r}" for k, v in sorted(record["params"].items())))))
        for note in record.get("notes", []):
            t.append((G, RDFS.comment, Literal(note)))
        for i in record.get("inputs", []):
            ref = i.get("ref")
            if isinstance(ref, str) and ref.startswith("repo:"):
                t.append((G, PROV.used, commit_url(commit, ref[5:])))
            elif isinstance(ref, str) and not ref.startswith("inputs:"):
                s, v, p = ref.split("/", 2)
                t += [(G, PROV.used, file_iri(s, v, p)), (V, PROV.wasDerivedFrom, version_iri(s, v))]
            elif isinstance(ref, str) and ref.startswith("inputs:"):
                pass   # described once per input below
            elif isinstance(ref, dict):   # the form of 0018, before the inputs area (0021)
                if is_url(ref.get("origin")):
                    t.append((G, PROV.used, IRI(ref["origin"])))
        for name, d in sorted((record.get("input_descriptions") or {}).items()):
            files = [i for i in record.get("inputs", []) if str(i.get("ref", "")).startswith(name + "/")]
            size = sum(i.get("bytes") or 0 for i in files)
            if is_url(d.get("origin")):
                t.append((G, PROV.used, IRI(d["origin"])))
            t.append((G, RDFS.comment, Literal(
                f"Input not published ({name}, {len(files)} file{'s' if len(files) != 1 else ''}, {size:,} bytes; "
                f"named by checksum in the run record): {d.get('title', '').strip()}. {d.get('description', '').strip()} "
                f"Origin: {d.get('origin', '').strip()}")))
    return t


def provenance(slug, vid, commit, now, dirty=()):
    """The provenance of the metadata itself: the rendering activity (ignored when deciding whether the content
    changed)."""
    M = IRI(f"{version_iri(slug, vid)}/metadata")
    t = [(file_iri(slug, vid, meta_path(slug)), PROV.wasGeneratedBy, M),
         (M, A, PROV.Activity),
         (M, PROV.wasAssociatedWith, IRI(software_iri(FRAMEWORK))),
         (M, PROV.endedAtTime, datetime(now)),
         (M, RDFS.comment, Literal("Rendered by the framework from the catalogue entry, the run record of the "
                                   "version and statistics measured on its files (decision 0018)."))]
    if commit:
        t.append((M, PROV.used, IRI(f"{REPO}/tree/{commit}")))
    return t


def content_lines(triples, slug, vid):
    """The canonical lines of the content part of a -meta (without the triples about or linking to the rendering
    activity)."""
    M = f"{version_iri(slug, vid)}/metadata"
    return sorted({nt_line(s, p, o, canonical=True) for s, p, o in triples if s != M and o != M})


def read_content(path, slug, vid):
    return content_lines(read_triples(path), slug, vid)
