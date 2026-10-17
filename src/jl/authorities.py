"""The authority datasets and how they select their records (decision 0029, the cascade).

An authority dataset (gnd, lc, geonames, wikidata, viaf) holds the records of one source that our datasets link to:
the record datasets and the other authority datasets (linking_inputs). It lists them in <slug>-selection.tsv.gz
(first column: the identifier, as linked). After every run of an authority dataset the framework lists the
identifiers of the other sources that the run names and that their datasets do not have yet (new_links, in the run
record as "authority_links"). Those datasets are run again, reading this run (jl generate --use), until no run names
new identifiers; then the runs become versions together (jl add-version with several runs). check(), the command
jl check-authorities, lists for every authority dataset the identifiers our datasets name that it does not have.

The cascade ends: an identifier is taken over once, and the identifiers of a source are only counted for the other
datasets, never for its own (a GND record that names another GND record does not select it).
"""

import gzip
from collections import defaultdict

from . import catalog, corrections, generator, identifiers, rdf, runs

# authority dataset -> its source (jl.identifiers)
SOURCE = {"gnd": "gnd", "lc": "lc-names", "geonames": "geonames", "wikidata": "wikidata", "viaf": "viaf"}
DATASET = {v: k for k, v in SOURCE.items()}
# datasets whose links never select records: made from the others (ep, quality-annotations), without links to records
# of a source, or replaced (gnd-persons); and our linksets to the authority datasets, which only link what these
# already have
NOT_LINKING = {"gnd-persons", "gnd-persons-entityfacts", "ep", "compact-memory", "compact-memory-supp", "cm-ocr-quality",
               "cm-tagme", "corrections-links", "quality-annotations", "judaicalink-agents", "judaicalink-vocabulary",
               "judaicalink-terms", "ontology"} | {"ls-" + s for s in SOURCE}
SELECTION = "{}-selection.tsv.gz"
EXAMPLES = 5


def linking_inputs(slug, add=None):
    """INPUTS of the datasets whose links select the records of the authority dataset slug: the stable versions (or
    the runs of jl generate --use) of all datasets except NOT_LINKING and slug itself, the other authority datasets
    included."""
    return generator.stable_inputs("linked_", exclude=NOT_LINKING | {slug}, add=add)


def selection_ref(cat, slug, use):
    """The version or run whose selection counts for slug: use (jl generate --use), else the stable version."""
    if slug in use:
        return use[slug]
    e = cat.get(slug)
    return e.stable if e else None


def selection_file(cfg, slug, ref):
    if ref is None:
        return None
    base = (cfg.require("build") if runs.is_run_id(ref) else cfg.require("store")) / slug / ref
    p = base / SELECTION.format(slug)
    return p if p.is_file() else None


def read_selection(path, source):
    """The identifiers of a selection file (first column), normalised as jl.identifiers does."""
    with gzip.open(path, "rt", encoding="utf-8") as f:
        next(f, None)
        return {identifiers.normal(source, line.split("\t", 1)[0]) for line in f if line.strip()}


def named(triples, sources=None):
    """{source: {identifier}} for the identifiers of authority sources the triples name as objects."""
    found = defaultdict(set)
    for _s, p, o in triples:
        x = identifiers.identify(o, p)
        if x and x[0] in DATASET and (sources is None or x[0] in sources):
            found[x[0]].add(x[1])
    return found


def compare(cfg, cat, found, use, own=None):
    """{dataset: {named, new, examples, selection}} for the sources in found (except own): what the datasets of the
    sources do not have."""
    out = {}
    for source, ids in sorted(found.items()):
        slug = DATASET[source]
        if slug == own:
            continue
        ref = selection_ref(cat, slug, use)
        path = selection_file(cfg, slug, ref)
        have = read_selection(path, source) if path else set()
        new = sorted(ids - have)
        out[slug] = {"named": len(ids), "new": len(new), "examples": new[:EXAMPLES],
                     "selection": f"{slug}/{ref}" if path else None}
    return out


def new_links(cfg, slug, directory, files, use):
    """For a run of the authority dataset slug: the identifiers of the other sources it names, and how many of them
    their datasets do not have (the stable version, or the run given with --use)."""
    found = defaultdict(set)
    for f in files:
        p = directory / f["path"]
        if rdf.rdf_format(p) is None or generator.is_meta(p):
            continue
        for source, ids in named(rdf.read_triples(p)).items():
            if source != SOURCE[slug]:
                found[source] |= ids
    return compare(cfg, catalog.Catalog(), found, use, own=slug)


def check(cfg, use=None, log=print):
    """For every authority dataset: the identifiers of its source that its linking datasets name and its selection
    lacks. Reads the stable versions (and use) once, with the deletions of the correction datasets."""
    use = use or {}
    cat = catalog.Catalog()
    deleted = set()
    for c_slug, c_version, c_path, _local in corrections.stable_deletions(cat):
        f = generator.resolve(cfg, cat, f"{c_slug}/{c_version}/{c_path}")[0]
        deleted.update(corrections.key(t) for t in corrections.read(f["path"]))
    generator.USE.clear()
    generator.USE.update(use)
    try:
        refs = generator.stable_inputs(exclude=NOT_LINKING)
    finally:
        generator.USE.clear()
    by_dataset = {}   # linking dataset -> {source: {identifier}}
    for ref in refs.values():
        slug = generator.slug_of(ref)
        found = defaultdict(set)
        for f in generator.resolve(cfg, cat, ref):
            ts = (t for t in rdf.read_triples(f["path"]) if not deleted or corrections.key(t) not in deleted)
            for source, ids in named(ts).items():
                found[source] |= ids
        by_dataset[slug] = found
        log(f"  read {ref}")
    out = {}
    for slug, source in SOURCE.items():
        ids = set().union(*(f.get(source, set()) for s, f in by_dataset.items() if s != slug))
        if ids or cat.get(slug):
            out.update(compare(cfg, cat, {source: ids}, use))
    return out
