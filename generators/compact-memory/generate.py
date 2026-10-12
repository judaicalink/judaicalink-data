"""compact-memory: the Compact Memory corpus (journals, volumes, issues, pages) of UB Frankfurt.

Transformation only, a port of cm_journals and cm_structure of kg-complements (datasets_deterministic.py,
2026-10-05; decision 0020) without changes to their logic, plus the image link of every page, which the 2021 version
stated and kg-complements had left to be derived, and classes: schema.org for volumes, issues and articles (from the
kind in the page table), jl:Page for pages. The sources: the page table (compact-memory-supp), the MODS records
of the nodes, the list of the OCR files (for the page IRIs) and the full-text bundle (which pages are in the full-text
index, with their date, label and journal). The pages of the version 2021-01-18 keep their IRIs.

Files: compact-memory-journals.ttl.gz (the corpus and its 336 journals), compact-memory-pages.ttl.gz (pages, volumes,
issues).
"""

import gzip
import html
import json
import re
from collections import Counter, defaultdict

from cm_sources import load_mods, mods_values, read_metadata, volume_from_mods
from jl.rdf import IRI, RDF_TYPE, XSD, Literal
from jl.turtle import PREFIXES

INPUTS = {
    "pages": "compact-memory-supp/2021-01-19/CM_Seiten_Metadaten.csv.gz",
    "mods": "inputs:compact-memory/mods-2020-06-15/",
    "ocr_paths": "inputs:compact-memory/ocr-paths-2026-10-05/",
    "fulltext": "inputs:compact-memory/fulltext-2026-10-05-v2/",
    "previous": "compact-memory/2021-01-18",
}
PARAMS = {}

JLO = PREFIXES["jl"]
DCT = PREFIXES["dcterms"]
FOAF = PREFIXES["foaf"]
OWL = PREFIXES["owl"]
RDFS = PREFIXES["rdfs"]
SCHEMA = PREFIXES["schema"]
CM = "http://data.judaicalink.org/data/compact-memory/"
VL = "http://sammlungen.ub.uni-frankfurt.de/cm/periodical/"
CORPUS = CM + "corpus"   # the corpus as a whole, e.g. for jl:CorpusPresence (decided 2026-10-12)
# classes for the kinds of nodes in the page table (Parent-Type); other kinds (chapter, correspondence, title page, …)
# get no class and keep their kind as dcterms:type (decided 2026-10-12)
KIND_CLASS = {"journal issue": SCHEMA + "PublicationIssue", "journal volume": SCHEMA + "PublicationVolume",
              "article": SCHEMA + "Article", "struct article": SCHEMA + "Article"}

_IRI_BAD = re.compile(r'[<>"{}|^`\\\s]')


def iri(value):
    """An IRI; characters not allowed in IRIs (from source data given as text) are percent-encoded."""
    return IRI(_IRI_BAD.sub(lambda m: "%{:02X}".format(ord(m.group(0))), value))


def lit(value, dt=None):
    return Literal(str(value), dt)


def integer(n):
    return Literal(str(n), XSD + "integer")


def date_literal(value):
    v = value.strip()
    for pat, dt in ((r"\d{4}-\d{2}-\d{2}", "date"), (r"\d{4}-\d{2}", "gYearMonth"), (r"\d{4}", "gYear")):
        if re.fullmatch(pat, v):
            return lit(v, XSD + dt)
    return lit(v)


class Triples:
    def __init__(self):
        self.t = set()

    def add(self, s, p, o):
        self.t.add((iri(s), iri(p), o if isinstance(o, Literal) else iri(o)))


# --- sources ---------------------------------------------------------------------------------------

def bundle_pages(run):
    """id -> (dateIssued, page_label, journal) for every page of the full-text bundle (its manifest lists the parts)."""
    files = {p.name: p for p in run.inputs("fulltext")}
    manifest = json.loads(files["manifest.json"].read_text(encoding="utf-8"))
    out = {}
    for part in manifest["parts"]:
        with gzip.open(files[part["file"]], "rt", encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                out[d["id"]] = (d.get("dateIssued"), d.get("page_label"), d["vlid_journal"])
    run.log(f"full-text bundle: {len(out):,} pages in {len(manifest['parts'])} parts")
    return out


def page_iris(run):
    """VLID_Seite -> page IRI, built like the existing compact-memory IRIs from the OCR file path
    (<dir>-<dir>-<dir>--<file prefix>-<VLID>). Several copies of one page: the first path in sort order.
    Pages that already have an IRI in the previous version keep it; where it has two (one per OCR file copy),
    the first in sort order is used and the others become owl:sameAs aliases."""
    paths = defaultdict(list)
    with gzip.open(run.input("ocr_paths"), "rt", encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^(.*)/(\d+)_(\d+)\.xml$", line.strip())
            if m:
                paths[m.group(3)].append((m.group(1), m.group(2)))
    pages = {v: CM + f"{sorted(ps)[0][0].replace('/', '-')}--{sorted(ps)[0][1]}-{v}" for v, ps in paths.items()}
    existing = defaultdict(set)
    for s, p, o in run.triples("previous"):
        if p == JLO + "hasVisualRepresentation" and "--" in s:
            existing[s.rsplit("-", 1)[-1]].add(str(s))
    aliases = {}
    for vid, found in existing.items():
        found = sorted(found)
        pages[vid] = found[0]
        if len(found) > 1:
            aliases[vid] = found[1:]
    run.log(f"page IRIs: {len(pages):,} from the OCR paths, {len(existing):,} kept from the previous version, "
            f"{len(aliases):,} with aliases")
    return pages, aliases


# --- journals --------------------------------------------------------------------------------------

def journals(rows, mods, bundle):
    """Journal descriptions from the MODS records of the UB Frankfurt, on the existing journal IRIs."""
    ids = sorted({r["VLID_Zs"].strip() for r in rows.values()}, key=int)
    indexed = Counter(j for (_d, _l, j) in bundle.values())
    w = Triples()
    w.add(CORPUS, RDF_TYPE, SCHEMA + "Collection")
    w.add(CORPUS, DCT + "title", lit("Compact Memory"))
    w.add(CORPUS, DCT + "description", lit("Jewish periodicals of the German-speaking countries, digitised by the "
                                           "University Library Frankfurt am Main (UB Frankfurt)."))
    w.add(CORPUS, FOAF + "page", "https://sammlungen.ub.uni-frankfurt.de/cm/")
    for jid in ids:
        x, j = mods.get(jid, ""), CM + jid
        w.add(j, RDF_TYPE, SCHEMA + "Periodical")
        w.add(j, DCT + "isPartOf", CORPUS)
        title_info = re.search(r"<titleInfo>(.*?)</titleInfo>", x, re.S)
        ti = title_info.group(1) if title_info else ""
        title = " ".join(v for v in (mods_values(ti, "nonSort") + mods_values(ti, "title")) if v)
        if title:
            w.add(j, DCT + "title", lit(title))
        for sub in mods_values(ti, "subTitle"):
            w.add(j, JLO + "subtitle", lit(sub))
        for origin in re.findall(r"<originInfo>(.*?)</originInfo>", x, re.S):
            if "Electronic ed." in origin:  # the digitisation, not the original publication
                continue
            for place in mods_values(origin, "placeTerm"):
                w.add(j, JLO + "placeOfPublication", lit(place))
            for pub in mods_values(origin, "publisher"):
                w.add(j, DCT + "publisher", lit(pub))
            for attrs, value in re.findall(r"<dateIssued([^>]*)>(.*?)</dateIssued>", origin, re.S):
                value = html.unescape(value).strip()
                if "keyDate" in attrs:
                    w.add(j, DCT + "issued", date_literal(value))
                else:
                    w.add(j, JLO + "publicationPeriod", lit(value))
        for code in re.findall(r'<languageTerm[^>]*type="code"[^>]*>([^<]+)<', x):
            w.add(j, DCT + "language", f"http://id.loc.gov/vocabulary/iso639-2/{code.strip()}")
        for kind, value in re.findall(r'<identifier type="([^"]+)">([^<]+)</identifier>', x):
            value = value.strip()
            w.add(j, DCT + "identifier", lit(f"{kind}:{value}"))
            if kind == "zdb":
                w.add(j, OWL + "sameAs", f"http://ld.zdb-services.de/resource/{value}")
            elif kind == "urn":
                w.add(j, RDFS + "seeAlso", f"https://nbn-resolving.org/{value}")
        w.add(j, FOAF + "page", VL + f"titleinfo/{jid}")
        w.add(j, JLO + "indexedPages", integer(indexed.get(jid, 0)))
    return w.t, len(ids)


# --- pages and nodes -------------------------------------------------------------------------------

def structure(run, rows, mods, bundle, pages, aliases):
    """Page -> issue/volume -> journal for every page of the full-text index."""
    w = Triples()
    nodes = {}
    kinds = {}
    missing_path = 0
    issue_dates = defaultdict(set)    # issue node -> dates of its pages
    page_date = {}                    # page IRI -> (issue node, date)
    for vid, (date, label, _journal) in bundle.items():
        r = rows[vid]
        p = pages.get(vid)
        if not p:
            missing_path += 1
            continue
        path = [n for n in r["OT_PATH"].strip("|").split("||") if n]
        w.add(p, RDF_TYPE, JLO + "Page")
        w.add(p, JLO + "belongsToIssue", CM + path[-2])
        w.add(p, JLO + "hasVisualRepresentation", VL + f"pageview/{vid}")
        for alias in aliases.get(vid, []):
            w.add(p, OWL + "sameAs", alias)
        if r["Seite (OT_SORT)"].strip().isdigit():
            w.add(p, JLO + "pageSequence", integer(int(r["Seite (OT_SORT)"])))
        if label:
            w.add(p, RDFS + "label", lit(label))
        if date:
            issue_dates[path[-2]].add(date[:10])
            page_date[p] = (path[-2], date[:10])
        for i in range(1, len(path) - 1):
            nodes[path[i]] = (path[i - 1], path[0])
        parent = r["VLID_Parent"].strip()
        if parent and r["Parent-Type"].strip():
            w.add(CM + parent, DCT + "type", lit(r["Parent-Type"].strip()))
            kinds[parent] = r["Parent-Type"].strip()
    # the date belongs to the issue; it stays on the pages only where the pages of one node have different dates
    dated_nodes = set()
    for node, dates in issue_dates.items():
        if len(dates) == 1:
            w.add(CM + node, DCT + "date", lit(next(iter(dates)), XSD + "date"))
            dated_nodes.add(node)
    mixed = 0
    for p, (node, date) in page_date.items():
        if node not in dated_nodes:
            w.add(p, DCT + "date", lit(date, XSD + "date"))
            mixed += 1
    classes = Counter()
    for node, (parent, journal) in nodes.items():
        n = CM + node
        # the class from the kind; a node without a kind directly below the journal is a volume
        cls = KIND_CLASS.get(kinds.get(node)) or (SCHEMA + "PublicationVolume"
                                                  if node not in kinds and parent == journal else None)
        if cls:
            w.add(n, RDF_TYPE, cls)
            classes[cls.rsplit("/", 1)[-1]] += 1
        w.add(n, DCT + "isPartOf", CM + parent)
        w.add(n, JLO + "belongsToJournal", CM + journal)
        w.add(n, FOAF + "page", VL + f"titleinfo/{node}")
        x = mods.get(node)
        if x:
            label = volume_from_mods(x)
            if label:
                w.add(n, RDFS + "label", lit(label))
            if node not in dated_nodes:   # nodes with pages: the (corrected) date of the full-text bundle
                for d in mods_values(re.search(r"<part>(.*?)</part>", x, re.S).group(1) if "<part>" in x else x,
                                     "date")[:1]:
                    w.add(n, DCT + "date", date_literal(d))
    run.log("classes: " + ", ".join(f"{c} {n:,}" for c, n in sorted(classes.items())))
    run.log(f"structure: {len(nodes):,} nodes, {mixed:,} pages with a date of their own, "
            f"{missing_path:,} pages of the bundle without an OCR path")
    if missing_path:
        run.note(f"{missing_path} page{'s' if missing_path != 1 else ''} of the full-text bundle without an OCR file "
                 "path left out.")
    if mixed:
        run.note(f"{mixed} page{'s' if mixed != 1 else ''} with a date of their own (the pages of their node have "
                 "different dates).")
    return w.t


def generate(run):
    rows = {r["VLID_Seite"].strip(): r for r in read_metadata(run.input("pages"))}
    run.log(f"page table: {len(rows):,} rows")
    mods = load_mods(run.input("mods"))
    run.log(f"MODS records: {len(mods):,}")
    bundle = bundle_pages(run)
    pages, aliases = page_iris(run)
    jt, n = journals(rows, mods, bundle)
    run.write_turtle("compact-memory-journals.ttl.gz", jt)
    run.write_turtle("compact-memory-pages.ttl.gz", structure(run, rows, mods, bundle, pages, aliases))
