"""The NLI authority export: reading, the kind of a record, record IRIs, the legacy URI assignment, matching works
to persons. Shared by the generators of nli-records and ls-nli-legacy (they share code, not runs, decision 0018).

Copied from nli_records.py of kg-complements (2026-10-06) without changes to its logic. The legacy generator
NLI-persons-03.py (2019) coined its URIs from the name heading and lost the record identity on the way:
- records with the same heading and the same date string share one URI (different people merged);
  homonyms get the suffixes 1 and 12 only, so the fourth and later homonyms merge again;
- the same person gets several URIs when the date strings differ ("1932-" vs "1932-2016");
- name/title records (works) and subject headings (name -- subdivision) became persons;
- records without a Latin heading reuse the heading of the record before (wrong name), dates without "-"
  reuse the dates of the record before;
- no identifier of the source record (the export carries the VIAF number in 901 and the LC number in 010).
"""

import gzip
import hashlib
import json
import re
from collections import defaultdict

JLD = "http://data.judaicalink.org/data/"
NLI = JLD + "nli/"
REC = NLI + "record/"
SCRIPT_LANG = {"lat": None, "heb": "he", "cyr": "und-Cyrl", "ara": "und-Arab"}
TITLE_CODES = set("tk")               # name/title heading: a work
SUBDIVISION_CODES = set("vxyz")       # name -- subdivision: a subject heading, not an entity of its own


# --------------------------------------------------------------------------- reading the export

def sub(field, code):
    return [v.strip() for v in field.get(code, []) if v and v.strip()]


def clean(s):
    """Heading text without MARC non-filing marks and trailing punctuation."""
    s = s.replace("<<", "").replace(">>", "")
    return re.sub(r"[\s,.:;/]+$", "", s).strip()


def heading(field, codes="abcq"):
    return clean(" ".join(v for c in codes for v in sub(field, c)))


def read_records(path):
    """All records of the export with a 100 field, in file order (the order the legacy generator used)."""
    out = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for n, line in enumerate(f):
            r = json.loads(line)
            if "100" in r:
                out.append((n, r))
    return out


def kind(r):
    codes = {c for f in r["100"] for c in f}
    if "t" in codes or "k" in codes:
        return "work"
    if codes & SUBDIVISION_CODES:
        return "subject-heading"
    return "person"


def record_iri(n, r, viaf_count):
    viaf = [a for x in r.get("901", []) for a in x.get("a", [])]
    if viaf and viaf_count[viaf[0]] == 1:
        return REC + "viaf-" + viaf[0]
    # no (unique) VIAF number: a hash of the headings, stable for this export
    return REC + "h-" + hashlib.sha1(json.dumps(r["100"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12]


# --------------------------------------------------------------------------- the legacy URIs

def legacy_assignment(records):
    """Reproduce NLI-persons-03.py exactly: the legacy URI, label and dates each record ended up with."""
    namedic = {}
    preflabel = pref = uriname = date = bd = dd = None
    result = []
    for n, record in records:
        titlelist = []
        namecount = 0
        fields = record["100"]
        has_lat = any(f["9"][0] == "lat" for f in fields if "9" in f) if len(fields) > 1 else True
        for i in range(len(fields)):
            if len(fields) > 1:
                if fields[i]["9"][0] == "lat":
                    preflabel = fields[i]["a"][0]
                    pref = preflabel.replace(".", "").replace("_", "")
            else:
                preflabel = fields[i]["a"][0]
                pref = preflabel.replace(".", "").replace("_", "")
            uriname = preflabel
            for a, b in (("'", ""), ('"', ""), (",", "_"), ("<<", ""), (">>", ""), ("|", "_"), (" ", ""),
                         ("<", "_"), (">", "_"), (".", "")):
                uriname = uriname.replace(a, b)
            if "t" in fields[i]:
                titlelist.append(fields[i]["t"][0])
            if "d" in fields[i]:
                date = fields[i]["d"][0]
                if "-" in date:
                    bd, dd = date.rsplit("-", 1)
            else:
                date = "NA"
        # a final date without "-" keeps the birth and death dates of an earlier record
        stale_dates = date != "NA" and "-" not in date
        stale_label = not has_lat
        if uriname not in namedic:
            uri = NLI + uriname
            namedic[uriname] = date
        elif date == namedic[uriname]:
            uri = NLI + uriname
        else:
            namecount += 1
            uriname = uriname + str(namecount)
            if uriname in namedic:
                if date == namedic[uriname]:
                    uri = NLI + uriname
                else:
                    namecount += 1
                    uriname = uriname + str(namecount)
                    uri = NLI + uriname
                    namedic[uriname] = date
            else:
                uri = NLI + uriname
                namedic[uriname] = date
        result.append({"uri": uri, "pref": pref, "date": date, "titles": titlelist,
                       "stale_label": stale_label, "stale_dates": stale_dates})
    return result


# --------------------------------------------------------------------------- matching works to persons

def person_index(records, viaf_count):
    """heading -> [(record IRI, date string)] for all person records, in all scripts."""
    index = defaultdict(list)
    for n, r in records:
        if kind(r) == "person":
            s = record_iri(n, r, viaf_count)
            for f in r["100"]:
                index[heading(f)].append((s, norm_date(f)))
    return index


def norm_date(field):
    return clean(" ".join(sub(field, "d"))).lower()


def named_person(r, index):
    """The one person record a work or subject heading names: same heading, compatible dates
    ("1932-" fits "1932-2016"); None if there is no such record or more than one."""
    found = set()
    for f in r["100"]:
        d = norm_date(f)
        cands = index.get(heading(f), [])
        exact = {s for s, pd in cands if pd == d}
        found |= exact or {s for s, pd in cands if d and pd.startswith(d.rstrip("-").strip()) or not d and len(cands) == 1}
    return next(iter(found)) if len(found) == 1 else None


def dates(r):
    """Birth and death date: the EDTF dates of 046 if present, else the years of the heading's $d."""
    birth = death = None
    for f in r.get("046", []):
        birth = birth or next(iter(sub(f, "f")), None)
        death = death or next(iter(sub(f, "g")), None)
    if not (birth or death):
        d = next((v for f in r["100"] for v in sub(f, "d") if f.get("9", [""])[0] == "lat"), None) \
            or next((v for f in r["100"] for v in sub(f, "d")), None)
        m = re.match(r"^(\d{3,4})\??\s*-\s*(\d{3,4})?\??[.,]?$", d or "")
        if m:
            birth, death = m.group(1), m.group(2)
    valid = lambda v: v if v and re.match(r"^-?\d{3,4}(-\d\d(-\d\d)?)?$", v) else None
    return valid(birth), valid(death)


def names(fields):
    """(text, language tag) of the headings, Latin script first."""
    out = []
    for f in fields:
        script = f.get("9", ["lat"])[0]
        text = heading(f)
        if text:
            out.append((text, SCRIPT_LANG.get(script, None) if script in SCRIPT_LANG else None, script))
    out.sort(key=lambda x: (x[2] != "lat", x[2]))
    return out


def identifiers(r):
    """The identifiers the export gives for a record: VIAF (901) and Library of Congress (010)."""
    out = ["http://viaf.org/viaf/" + a for x in r.get("901", []) for a in x.get("a", [])][:1]
    out += ["http://id.loc.gov/authorities/names/" + a.replace(" ", "") for f in r.get("010", []) for a in sub(f, "a")]
    return out
