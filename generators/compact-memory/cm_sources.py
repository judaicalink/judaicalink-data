"""Reading the Compact Memory sources of UB Frankfurt: the page table and the MODS records.

Copied from extract_cm_fulltext.py (cm_indexer in the repository of the FID portal; the same file is in the input
inputs:compact-memory/fulltext-2026-10-05-v2), which made the full-text bundle: read_metadata (here also for a gzipped
CSV), load_mods, mods_values and volume_from_mods, unchanged otherwise, so that labels and dates are read exactly as
for the bundle.
"""

import csv
import gzip
import html
import io
import re
import zipfile
from pathlib import Path


def read_metadata(path):
    """The rows of CM_Seiten_Metadaten.csv (tab-separated), plain or gzipped."""
    path = Path(path)
    opener = gzip.open if path.name.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def load_mods(path):
    """Node id -> MODS XML, from CM_Knoten_MODS_XML_* or the zip that contains it."""
    path = Path(path)
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as z:
            name = next(n for n in z.namelist() if "MODS" in n)
            raw = z.read(name).decode("utf-8-sig")
    else:
        raw = path.read_text(encoding="utf-8-sig")
    csv.field_size_limit(1 << 30)
    rows = csv.reader(io.StringIO(raw, newline=""), delimiter="\t")
    next(rows)
    return {r[0]: r[1] for r in rows if len(r) >= 2}


def mods_values(xml, tag):
    return [re.sub(r"\s+", " ", html.unescape(v)).strip()
            for v in re.findall(rf"<{tag}(?:\s[^>]*)?>(.*?)</{tag}>", xml, re.S)]


def volume_from_mods(xml):
    """Volume label as the 2020 export built it: caption, else "number (date)", plus the volume
    title. Reproduces 99.9% of the volume values in the CSV that are not the filler."""
    part = re.search(r"<part>(.*?)</part>", xml, re.S)
    xml = part.group(1) if part else xml
    first = lambda tag: (mods_values(xml, tag) or [None])[0]
    number, caption, title = first("number"), first("caption"), first("title")
    dates = mods_values(xml, "date")
    date = "-".join(dates[:2]) if dates else None
    base = caption or (f"{number} ({date})" if number and date else number or date)
    if title and base and title in base:
        title = None
    label = " ".join(v for v in (base, title) if v)
    return re.sub(r"\s+", " ", label).strip() or None
