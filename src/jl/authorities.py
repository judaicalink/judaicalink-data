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
        if rdf.rdf_format(f["path"]) is None or generator.is_meta(f["path"]):
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


# --- the links between the authority datasets ------------------------------------------------------

WDTN = "http://www.wikidata.org/prop/direct-normalized/"
# the properties by which an authority record states that it is the same as a record of another source
IDENTITY = {"http://www.w3.org/2002/07/owl#sameAs", "http://www.w3.org/2004/02/skos/core#exactMatch",
            "http://www.loc.gov/mads/rdf/v1#hasExactExternalAuthority", *identifiers.LITERAL_PROPERTIES,
            WDTN + "P227", WDTN + "P214", WDTN + "P244", WDTN + "P1566"}
REPLACED = "http://purl.org/dc/terms/isReplacedBy"
DEPRECATED = "http://www.w3.org/2002/07/owl#deprecated"


class Authority:
    """What one authority dataset says: its records, replacements and deprecations, and the identity links of its
    records to the other sources."""

    def __init__(self, source):
        self.source = source
        self.records, self.deprecated = set(), set()
        self.replaced = defaultdict(set)
        self.links = defaultdict(lambda: defaultdict(set))   # id -> source -> {id}

    def read(self, triples):
        for s, p, o in triples:
            x = identifiers.identify(s)
            if not x or x[0] != self.source:
                continue
            ident = x[1]
            if p == REPLACED:
                y = identifiers.identify(o)
                if y and y[0] == self.source:
                    self.replaced[ident].add(y[1])
                continue
            if p == DEPRECATED and isinstance(o, rdf.Literal) and o.value == "true":
                self.deprecated.add(ident)
                continue
            self.records.add(ident)
            if p in IDENTITY:
                y = identifiers.identify(o, p)
                if y and y[0] in DATASET and y[0] != self.source:
                    self.links[ident][y[0]].add(y[1])

    def current(self, ident):
        """(current identifiers, status): status current, replaced, deprecated, or not in the dataset (not selected
        yet, or not in the source: the selection says which)."""
        seen, todo, out = set(), [ident], set()
        while todo:
            i = todo.pop()
            if i in seen:
                continue
            seen.add(i)
            if self.replaced.get(i):
                todo.extend(self.replaced[i])
            elif i in self.records and i not in self.deprecated:
                out.add(i)
        status = ("current" if ident in self.records and ident not in self.deprecated and not self.replaced.get(ident)
                  else "replaced" if self.replaced.get(ident) else "deprecated" if ident in self.deprecated
                  else "not in the dataset")
        return out, status


def check_links(cfg, use=None, log=print):
    """The identity links between the authority datasets (the stable versions, or use): per pair of sources, the
    records that link to several records of the other source, to an identifier it does not hold as current
    (replaced, deprecated, unknown), whose link the other side does not return (it links back to another record),
    and the chains A -> B -> C -> A' that come back to another record. Returns ({finding: count}, [rows])."""
    use = use or {}
    cat = catalog.Catalog()
    data = {}
    for slug, source in SOURCE.items():
        ref = selection_ref(cat, slug, use)
        if ref is None:
            continue
        a = Authority(source)
        for f in generator.resolve(cfg, cat, f"{slug}/{ref}"):
            a.read(rdf.read_triples(f["path"]))
        data[source] = a
        log(f"  read {slug}/{ref}: {len(a.records):,} records")
    counts, rows = defaultdict(int), []

    def note(kind, a_src, b_src, detail, *ex):
        key = f"{kind}: {DATASET[a_src]} -> {DATASET[b_src]}" + (f" -> {detail}" if detail else "")
        counts[key] += 1
        rows.append((kind, DATASET[a_src], DATASET[b_src], detail or "", *ex))

    def resolve(src, ident):
        return data[src].current(ident)[0] if src in data else {ident}

    for a_src, a in data.items():
        for a_id, by_source in a.links.items():
            if a_id in a.deprecated or a.replaced.get(a_id):
                continue
            for b_src, b_ids in by_source.items():
                cur, missing = set(), False
                for b_id in b_ids:
                    c, status = data[b_src].current(b_id) if b_src in data else ({b_id}, "current")
                    if status != "current":
                        note("not current", a_src, b_src, status, a_id, b_id, " ".join(sorted(c)))
                    missing = missing or status == "not in the dataset"
                    cur |= c
                if len(cur) > 1:
                    note("several", a_src, b_src, "", a_id, " ".join(sorted(cur)), "")
                elif len(b_ids) > 1:
                    note("several, not all in the dataset" if missing else "several, the same after replacement",
                         a_src, b_src, "", a_id, " ".join(sorted(b_ids)), "")
                if b_src not in data:
                    continue
                for b_id in cur:
                    back = set()
                    for x in data[b_src].links.get(b_id, {}).get(a_src, ()):
                        back |= resolve(a_src, x)
                    if back and a_id not in back:
                        note("not returned", a_src, b_src, "", a_id, b_id, " ".join(sorted(back)))
                    for c_src, c_ids in data[b_src].links.get(b_id, {}).items():
                        if c_src in (a_src, b_src) or c_src not in data:
                            continue
                        for c_id in set().union(*(resolve(c_src, c) for c in c_ids)):
                            other = set()
                            for x in data[c_src].links.get(c_id, {}).get(a_src, ()):
                                other |= resolve(a_src, x)
                            if other and a_id not in other:
                                note("chain", a_src, b_src, DATASET[c_src], a_id, f"{b_id} {c_id}",
                                     " ".join(sorted(other)))
    return dict(sorted(counts.items())), rows
