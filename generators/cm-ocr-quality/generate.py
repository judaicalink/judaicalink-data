"""cm-ocr-quality: an estimate of the OCR quality of every Compact Memory page, and the mean per journal.

Transformation only, a port of cm_ocr_quality of kg-complements (datasets_deterministic.py, 2026-10-05; decision 0020)
without changes to its logic. Per page: the share of its words (letters only, at least 2 characters, lowercased) that
occur at least 10 times in every 20th page of the corpus. The page IRIs are those of compact-memory 2026-10-12.
"""

import gzip
import json
import re
from collections import Counter, defaultdict

from jl.rdf import IRI, RDF_TYPE, XSD, Literal
from jl.turtle import PREFIXES

INPUTS = {
    "fulltext": "inputs:compact-memory/fulltext-2026-10-05-v2/",
    "pages": "compact-memory/2026-10-12/compact-memory-pages.ttl.gz",
}
PARAMS = {}

JLO = PREFIXES["jl"]
CM = "http://data.judaicalink.org/data/compact-memory/"
WORD_RE = re.compile(r"[^\W\d_]{2,}")


def decimal(value):
    return Literal(f"{value:.4f}", XSD + "decimal")


def bundle_texts(run):
    """id -> (journal, text) for every page of the full-text bundle."""
    files = {p.name: p for p in run.inputs("fulltext")}
    manifest = json.loads(files["manifest.json"].read_text(encoding="utf-8"))
    out = {}
    for part in manifest["parts"]:
        with gzip.open(files[part["file"]], "rt", encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                out[d["id"]] = (d["vlid_journal"], d["text"])
    run.log(f"full-text bundle: {len(out):,} pages")
    return out


def generate(run):
    bundle = bundle_texts(run)
    pages = {str(s).rsplit("-", 1)[-1]: s for s, p, o in run.triples("pages")
             if p == RDF_TYPE and o == JLO + "Page"}
    run.log(f"pages of compact-memory: {len(pages):,}")
    counts = Counter()
    for k, (_journal, text) in bundle.items():
        if int(k) % 20 == 0:
            counts.update(WORD_RE.findall(text.lower()))
    lex = {t for t, n in counts.items() if n >= 10}
    run.note(f"Word list: {len(lex):,} words occurring at least 10 times in every 20th page.")
    t = []
    per_journal = defaultdict(list)
    for vid, (journal, text) in bundle.items():
        toks = WORD_RE.findall(text.lower())
        q = sum(tok in lex for tok in toks) / len(toks) if toks else 0.0
        if vid in pages:
            t.append((pages[vid], IRI(JLO + "ocrKnownWordShare"), decimal(round(q, 4))))
        per_journal[journal].append(q)
    for journal, qs in per_journal.items():
        t.append((IRI(CM + journal), IRI(JLO + "meanOcrKnownWordShare"), decimal(round(sum(qs) / len(qs), 4))))
    run.write_turtle("cm-ocr-quality.ttl.gz", t)
