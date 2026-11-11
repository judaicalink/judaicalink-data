"""records-normalized: normalised values for the literals of the record datasets: dates, places, occupations.

Transformation only, a port of four builders of kg-complements (2026-10-06; decision 0020) without changes to their
logic (except the date rules, below): dates_normalized and places_linked (datasets_algorithmic.py), occupation_concepts and occupation_fix
(datasets_deterministic.py). They queried "all graphs" of the endpoint; here the inputs are the stable versions of
the datasets that hold the values they read (RECORD_SLUGS, PLACE_SLUGS). Facts about records, never about entity
pages (0008).

Files:
- records-normalized-dates.ttl.gz: jl:birthDateNormalized / jl:deathDateNormalized (xsd:date, gYearMonth, gYear) for the
  free-text jl:birthDate / jl:deathDate, with jl:birthDateUncertain / jl:deathDateUncertain. The rules of the port
  were extended on 2026-10-12, before the first version was published, for the forms that quality-annotations found
  left out: English dates (October 28, 1905), year and month (1914-11), dateTimes, 1942-- and 1347-06/07 (the year),
  XX.10.1944, 9.1749, years 1–999, Hebrew years as numbers (5676) and Hebrew-Gregorian pairs (5559-1798), equal years
  (1831-1831), the EDTF value of the footprints dictionaries, German dates (17. Sept. 1834, 23. März 1963, März 1963,
  also with a remark after the date; 2026-11-11); a record whose one death date is before its one
  birth date gets neither. Ranges, bounds (vor 1593) and years before the common era stay out;
- records-normalized-places.ttl.gz: jl:birthLocationURI / jl:deathLocationURI for the text places, where a dictionary
  gives exactly one IRI (pairs already in the data, places of cm-entities, places of rujen and geo-coordinates);
- records-normalized-occupations.ttl.gz: jl:occupationURI for text occupations equal to the name of an occupation IRI
  used in the data (also those stated as jl:occupationURI), and for every occupation IRI that a record states with
  jl:occupation or the misspelt jl:occpation
  (bhr), against the literal range of jl:occupation (decided 2026-10-12): one property for all occupation IRIs.

With the parameter legacy_terms, the terms and files of kg-complements instead (jl:occupationConcept; the typo fix as
jl:occupation in records-normalized-occupation-fix.ttl.gz), to check the port against its output.
"""

import re
import unicodedata
from collections import Counter, defaultdict
from urllib.parse import unquote

from jl import classes
from jl import dates as jldates
from jl.generator import slug_of, stable_inputs
from jl.rdf import IRI, RDF_TYPE, XSD, Literal
from jl.turtle import PREFIXES

# the stable versions of the record datasets and of the datasets of the place dictionaries (since 2026-11-10; the
# versions were pinned before, and records-normalized 2026-10-12 still read geo-enriched 2019 after its replacement)
RECORD_SLUGS = {"bhr", "dbpedia", "djh", "epidat", "footprints", "geo-enriched", "gnd", "haskala", "hhkeydocs",
                "hirsch-family", "jre", "nli-records", "sosy", "ubffm-persons"}
PLACE_SLUGS = {"rujen", "geo-coordinates", "cm-entities"}
_STABLE = stable_inputs(kinds=None)
RECORDS = {k: v for k, v in _STABLE.items() if slug_of(v) in RECORD_SLUGS}
PLACES = {k: v + ("/cm-entities-wikidata.ttl.gz" if slug_of(v) == "cm-entities" else "")
          for k, v in _STABLE.items() if slug_of(v) in PLACE_SLUGS}
INPUTS = {**RECORDS, **PLACES}
PARAMS = {"legacy_terms": False}

JLO = PREFIXES["jl"]
SKOS = PREFIXES["skos"]
EP = "http://data.judaicalink.org/data/ep/"
_IRI_BAD = re.compile(r'[<>"{}|^`\\\s]')


def iri(value):
    return IRI(_IRI_BAD.sub(lambda m: "%{:02X}".format(ord(m.group(0))), value))


def lit(value, dt=None):
    return Literal(str(value), dt)


# --- dates (from datasets_algorithmic.py, with more forms, 2026-10-12) -------------------------------

HEBREW_VALUES = {"א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5, "ו": 6, "ז": 7, "ח": 8, "ט": 9, "י": 10, "כ": 20, "ך": 20,
                 "ל": 30, "מ": 40, "ם": 40, "נ": 50, "ן": 50, "ס": 60, "ע": 70, "פ": 80, "ף": 80, "צ": 90, "ץ": 90,
                 "ק": 100, "ר": 200, "ש": 300, "ת": 400}
# approximate dates; "vor"/"nach" (before/after) are bounds, not approximations, and stay unparsed
UNCERTAIN = re.compile(r"\?|\bca\.?|\bum\b|\bcirca\b|\bc\.\s|בערך|~|\bvermutlich\b|\bwahrscheinlich\b|\bvielleicht\b|\betwa\b|\bprobably\b|\[sic!?\]", re.I)
# a Hebrew year in letters is one word with geresh/gershayim: תרע"ג, ה'תרע"ג, תר״ס
HEBREW_YEAR_RE = re.compile(r"^(?:[א-ת]['׳])?[א-ת]{1,3}[\"״][א-ת]$")
# footprints writes some dates as Python dictionaries: {'id': 996, 'edtf_format': '1663/1711', 'display': '1663 - 1711'}
DICT_DATE = re.compile(r"^\{.*'edtf_format': '([^']*)'")
MONTHS = {m: i for i, m in enumerate(("january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"), 1)}
# German month names, written out and abbreviated (17. Sept. 1834, 23. März 1963; decided 2026-11-11)
MONATE = {**{m: i for i, m in enumerate(("januar", "februar", "märz", "april", "mai", "juni", "juli", "august",
                                         "september", "oktober", "november", "dezember"), 1)},
          "jänner": 1, "jan": 1, "jän": 1, "feb": 2, "febr": 2, "mrz": 3, "mär": 3, "apr": 4, "jun": 6, "jul": 7,
          "aug": 8, "sep": 9, "sept": 9, "okt": 10, "nov": 11, "dez": 12}
GERMAN_DATE = re.compile(r"(?:(\d{1,2})\.?\s*)?([A-Za-zÄäÖöÜü]+)(?:\.\s*|\s+)(\d{4})")   # Sep, Sept., 17.Sept.1834
YEARS = (1, 2030)   # years before the common era (-0126) are left out: standards number them differently
HEBREW_YEARS = (5000, 5800)   # a year written as a number in this span is a Hebrew year (anno mundi)


def hebrew_year(s):
    """Hebrew year in letters (e.g. תרע"ג) -> Gregorian year, assuming the 6th millennium (5000+)."""
    letters = re.sub(r"[\"'״׳\s]", "", s)
    if letters.startswith("ה") and len(letters) > 3:  # explicit thousands: ה'תרע"ג
        letters = letters[1:]
    if not letters or any(ch not in HEBREW_VALUES for ch in letters):
        return None
    value = sum(HEBREW_VALUES[ch] for ch in letters)
    return 5000 + value - 3760 if 100 <= value <= 799 else None


def ymd(y, mo=None, d=None):
    """The most precise literal for a year, month and day (a day or month out of range is dropped)."""
    if mo and 1 <= mo <= 12:
        if d and 1 <= d <= 31:
            return lit(f"{y:04d}-{mo:02d}-{d:02d}", XSD + "date")
        return lit(f"{y:04d}-{mo:02d}", XSD + "gYearMonth")
    return lit(f"{y:04d}", XSD + "gYear")


def normalize_date(raw):
    """Free-text date -> (literal, uncertain) or None."""
    s = raw.strip()
    m = DICT_DATE.match(s)
    if m:   # the EDTF value of a footprints dictionary (EDTF marks approximate and uncertain dates with ~ and ?)
        s = m.group(1)
    uncertain = bool(UNCERTAIN.search(s))
    bracketed = bool(re.fullmatch(r"\[.*\]", s))   # supplied by the cataloguer
    core = UNCERTAIN.sub(" ", s).strip(" .,[]()")
    uncertain = uncertain or bracketed
    m = re.fullmatch(r"(\d{3,4})-(\d{2})-(\d{2})(?:T[\d:.]+Z?)?", core)   # ISO date, also as a dateTime
    if m:
        return ymd(*map(int, m.groups())), uncertain
    m = re.fullmatch(r"(\d{3,4})-(\d{2})-*", core)   # year and month (epidat also 1925-03-)
    if m and 1 <= int(m.group(2)) <= 12:
        return ymd(*map(int, m.groups())), uncertain
    m = re.fullmatch(r"(\d{4})-(\d{2})/(\d{2})", core)   # one of two months: the year is known
    if m:
        return ymd(int(m.group(1))), uncertain
    m = re.fullmatch(r"(\d{4})-+", core)   # month and day unknown (epidat: 1942--)
    if m:
        return ymd(int(m.group(1))), uncertain
    m = re.fullmatch(r"(\d{1,2}|XX)\.\s?(\d{1,2}|XX)\.\s?(\d{4})", core)   # D.M.YYYY, XX for unknown parts
    if m:
        d, mo, y = (None if x == "XX" else int(x) for x in m.groups())
        if d is None or mo is not None:
            return ymd(y, mo, d if mo else None), uncertain
    m = re.fullmatch(r"(\d{1,2})\.(\d{4})", core)   # M.YYYY
    if m and 1 <= int(m.group(1)) <= 12:
        return ymd(int(m.group(2)), int(m.group(1))), uncertain
    m = GERMAN_DATE.fullmatch(core)   # German: 17. Sept. 1834, 23. März 1963, März 1963
    if not m:   # the date followed by a remark: 18. Juli 1823 das …, 16. Juni 1902 auf der Reise …
        m = GERMAN_DATE.match(core)
        rest = core[m.end():] if m and m.group(1) else ""
        if not (rest[:1].isspace() and re.match(r"\s+[A-Za-zÄäÖöÜü]", rest) and not re.search(r"\boder\b|[-–/]\s*\d", rest)):
            m = None
    if m and m.group(2).lower() in MONATE:
        d = int(m.group(1)) if m.group(1) else None
        return ymd(int(m.group(3)), MONATE[m.group(2).lower()], d), uncertain
    m = re.fullmatch(r"([A-Za-z]+)\.? (\d{1,2}), (\d{4})", core)   # English: October 28, 1905
    if m and m.group(1).lower() in MONTHS:
        return ymd(int(m.group(3)), MONTHS[m.group(1).lower()], int(m.group(2))), uncertain
    m = re.fullmatch(r"(\d{4})\s*[-/]\s*(\d{4})", core)
    if m:
        a, b = map(int, m.groups())
        if a == b:   # 1831-1831
            return ymd(a), uncertain
        if HEBREW_YEARS[0] < a < HEBREW_YEARS[1] and b - (a - 3760) in (0, 1):   # Hebrew and Gregorian: 5559-1798
            return ymd(b), uncertain
        return edtf_date(core, uncertain, s)
    m = re.fullmatch(r"\d{3,4}", core)
    if m:
        y = int(core)
        if HEBREW_YEARS[0] < y < HEBREW_YEARS[1]:
            return ymd(y - 3760), True   # a Hebrew year spans two Gregorian years
        return ymd(y), uncertain
    if HEBREW_YEAR_RE.match(core):
        y = hebrew_year(core)
        if y:
            return lit(str(y), XSD + "gYear"), True  # a Hebrew year spans two Gregorian years
    return edtf_date(core, uncertain, s)


# --- EDTF (decision 0035) and Hebrew dates (decided 2026-11-11) --------------------------------------

BOUNDS = {"vor": "before", "before": "before", "bis": "before", "nach": "after", "after": "after", "ab": "after",
          "seit": "after"}
HEBREW_DATE = re.compile(r"(?:(\d{1,2})\.?\s*)?(" + "|".join(sorted(jldates.HEBREW_MONTHS, key=len, reverse=True))
                         + r")\.?\s+(\d{4})(?:\s*/\s*(\d{2,4}))?", re.I)


def edtf(value):
    return lit(value, jldates.EDTF)


def full_year(a, b):
    """The second year of a pair written short: 1944/45 -> 1945."""
    if len(b) < 4:
        b = a[:4 - len(b)] + b
    return int(b)


def edtf_date(core, uncertain, raw=""):
    """The forms only EDTF expresses: unknown digits (194X), ranges (1610-1624, 1944/45), bounds (vor 1722), and
    Hebrew dates as Gregorian dates or intervals. (literal, uncertain) or None."""
    m = re.fullmatch(r"\[?(\d{4})\?-(\d{2})-(\d{2})\]?", raw.strip())   # a doubtful year in an ISO date: 1863?-10-22
    if m:
        return ymd(*map(int, m.groups())), True
    m = re.fullmatch(r"(\d{4})\s*~\s*(\d{4})", raw.strip())   # 1670~1720: about these years
    if m and int(m.group(1)) < int(m.group(2)):
        return edtf(f"{m.group(1)}/{m.group(2)}"), True
    s = core.strip(" „“\"'")
    rest = re.sub(r"^(?:am|im|den|der)\s+", "", s, flags=re.I)   # am 16. Februar 1859
    if rest != s:
        inner = normalize_date(rest)
        return (inner[0], uncertain or inner[1]) if inner else None
    m = re.fullmatch(r"(\d{2})([\dXx])([Xx])|(\d{3})([Xx])|(1)([Xx]{3})", s)   # unknown digits: 19XX, 194X, 1XXX
    if m:
        return edtf(s.upper()), uncertain
    m = re.fullmatch(r"(\d{3})0er(?: Jahre)?", s)   # 1870er
    if m:
        return edtf(m.group(1) + "X"), uncertain
    m = re.fullmatch(r"(?:(anfang|mitte|ende)\s+(?:des\s+)?)?(\d{1,2})(?:\.\s*(?:jh|jhs|jahrhunderts?)\.?|(?:st|nd|rd|th)\s+century)",
                     s, re.I)   # 18. Jh., 19th century, Mitte des 19. Jhs.: the hundred years 1800-1899
    if m and 1 <= int(m.group(2)) <= 21:
        return edtf(f"{int(m.group(2)) - 1:02d}XX"), uncertain or bool(m.group(1))
    m = re.fullmatch(r"(frühjahr|frühling|sommer|herbst|winter)\s+(\d{4})", s, re.I)   # EDTF seasons 21-24
    if m:
        season = {"frühjahr": 21, "frühling": 21, "sommer": 22, "herbst": 23, "winter": 24}[m.group(1).lower()]
        return edtf(f"{m.group(2)}-{season}"), uncertain
    m = re.fullmatch(r"(?:anfang|mitte|ende|beginn)\s+(\d{4})", s, re.I)   # Ende 1849: the year
    if m:
        return ymd(int(m.group(1))), uncertain
    m = re.fullmatch(r"(\d{1,2})\./(\d{1,2})\.\s*(\S+?)\.?\s+(\d{4})", s)   # 13./14. Sept. 1828: one night
    if m and m.group(3).lower().rstrip(".") in MONATE and int(m.group(2)) == int(m.group(1)) + 1:
        mo, y = MONATE[m.group(3).lower().rstrip(".")], int(m.group(4))
        a, b = ymd(y, mo, int(m.group(1))), ymd(y, mo, int(m.group(2)))
        if a.datatype == b.datatype == XSD + "date":
            return edtf(f"{a.value}/{b.value}"), uncertain
    m = re.fullmatch(r"(\d{4})\.(\d{2})\.(\d{2})", s)   # 1898.02.28
    if m:
        return ymd(*map(int, m.groups())), uncertain
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s)   # 04/01/1786: day and month in an unknown order
    if m:
        return ymd(int(m.group(3))), uncertain
    m = re.fullmatch(r"(\d{4})-+(\d{2})", s)   # 1880--10: the month unknown
    if m:
        return ymd(int(m.group(1))), uncertain
    m = re.fullmatch(r"\[?(\d{4})\?-(\d{2})\]?", (raw or s).strip())   # 1839?-06
    if m:
        return ymd(int(m.group(1)), int(m.group(2))), True
    m = re.fullmatch(r"(\d{4}),\s*(vor|nach)", s, re.I)   # 1739, nach
    if m:
        return edtf(f"../{m.group(1)}" if m.group(2).lower() == "vor" else f"{m.group(1)}/.."), uncertain
    m = re.fullmatch(r"(\d{4})\s+(?:das|im|in|zu|ebd)\b.*", s)   # 1886 das …, 1757 im Elsaß: the year
    if m and not re.search(r"\boder\b", s):
        return ymd(int(m.group(1))), uncertain
    m = re.fullmatch(r"(\d{4})\?-(\d{2})-(\d{2})", s)   # a doubtful year in an ISO date: 1863?-10-22
    if m:
        return ymd(*map(int, m.groups())), True
    m = re.fullmatch(r"(\d{4})\s*[-–/~]\s*(\d{2,4})", s)   # a range of years
    if m:
        a, b = int(m.group(1)), full_year(m.group(1), m.group(2))
        if a < b <= a + 200:
            return edtf(f"{a:04d}/{b:04d}"), uncertain
        return None
    m = re.fullmatch(r"(vor|before|bis|nach|after|ab|seit)\s+(?:dem\s+|the\s+)?(.+)", s, re.I)   # a bound
    if m:
        inner = normalize_date(m.group(2))
        if inner and inner[0].datatype != jldates.EDTF:
            v = inner[0].value
            return edtf(f"../{v}" if BOUNDS[m.group(1).lower()] == "before" else f"{v}/.."), uncertain or inner[1]
        return None
    base = (raw or s).strip()
    stripped = re.sub(r"\s*[(\[][^)\]]*[)\]]", "", base).strip(" .„“\"")   # remarks in brackets: the date outside counts
    if stripped != base.strip(" .„“\"") and stripped:
        doubt = bool(re.search(r"\?|vielleicht|vermutlich|lt\.|nach\s+\w+:|oder", base, re.I))
        inner = normalize_date(stripped)
        if inner:
            return inner[0], uncertain or inner[1] or doubt
    m = HEBREW_DATE.search(s)
    if m and not re.search(r"\boder\b", s):
        return hebrew_date(m, uncertain)
    return None


def hebrew_date(m, uncertain):
    """A Hebrew day and month with a year: a Hebrew year (5000-5800), a Gregorian one (the Hebrew year that puts the date
    into it), or a pair (Kislew 1836/37: the Hebrew year that begins in the first). Without a day: the month as an EDTF
    interval. Adar without I or II in a leap year, a day that does not exist, or two dates in one year: the year only."""
    day = int(m.group(1)) if m.group(1) else None
    month = jldates.HEBREW_MONTHS[m.group(2).lower()]
    y = int(m.group(3))
    if HEBREW_YEARS[0] < y < HEBREW_YEARS[1]:
        candidates, gregorian = [y], None
    elif m.group(4):
        candidates, gregorian = [y + 3761], None
    else:
        candidates, gregorian = [y + 3760, y + 3761], y
    found, adar = [], False
    for hy in candidates:
        if month == 12 and jldates.hebrew_leap(hy) and m.group(2).lower() == "adar":
            adar = True   # Adar I or Adar II: the Gregorian year is still certain
            continue
        mo = 13 if month == 13 and not jldates.hebrew_leap(hy) else month
        if mo == 13 and not jldates.hebrew_leap(hy):
            mo = 12
        if day:
            g = jldates.hebrew_to_gregorian(hy, mo, day)
            if g and (gregorian is None or g.year == gregorian):
                found.append((g, g))
        else:
            first = jldates.hebrew_to_gregorian(hy, mo, 1)
            last = jldates.hebrew_to_gregorian(hy, mo, jldates.hebrew_month_days(hy, mo))
            if gregorian is None or gregorian in (first.year, last.year):
                found.append((first, last))
    if len(found) == 1:
        a, b = found[0]
        if a == b:
            return ymd(a.year, a.month, a.day), uncertain
        return edtf(f"{a.isoformat()}/{b.isoformat()}"), uncertain
    if gregorian:
        return ymd(gregorian), uncertain or not (found or adar)
    return None


def years_of(value):
    """(earliest, latest) year of a normalised value; None for an open end; X as 0 and 9."""
    ends = value.value.split("/")
    out = []
    for e in (ends[0], ends[-1]):
        m = re.match(r"-?([0-9Xx]{4})", e)
        out.append(m.group(1) if m else None)
    lo = int(out[0].upper().replace("X", "0")) if out[0] else None
    hi = int(out[1].upper().replace("X", "9")) if out[1] else None
    return lo, hi


def year_of(value):
    lo, hi = years_of(value)
    return lo if lo is not None else hi


def parse_date(raw):
    """normalize_date, with years outside YEARS left out: (literal, uncertain) or None. Also used by
    quality-annotations for the dates left out (shared code)."""
    result = normalize_date(raw)
    if result and all(y is None or YEARS[0] <= y <= YEARS[1] for y in years_of(result[0])):
        return result
    return None


def why_not(raw):
    """Why a date is left out, for quality-annotations (or None: no recognised form)."""
    s = raw.strip()
    m = DICT_DATE.match(s)
    if m:
        return f"a Python dictionary written as text, whose EDTF value '{m.group(1)}' is not a single date"
    if re.fullmatch(r"-\d+(-\d\d){0,2}", s):
        return ("a negative year: before the common era (left out, standards number these years differently) or the end "
                "of an open range")
    if re.match(r"(vor|nach|before|after|bis|ab)\b", s, re.I):
        return "a bound (before or after), not a date"
    if re.search(r"\d{3,4}(-\d\d)?\s*[-–/~]\s*\d{2,4}", s):
        return "a range, not a single date"
    result = normalize_date(s)
    if result:
        return f"the year {year_of(result[0])} is outside {YEARS[0]}–{YEARS[1]}"
    return None


def dates(run, values):
    """The normalised dates; a record whose death is before its birth gets neither (e.g. years before the common era
    written without a minus sign: Aeschylus 0525–0456)."""
    t = set()
    stats = Counter()
    unparsed = []
    parsed = defaultdict(lambda: defaultdict(list))
    for prop in ("birthDate", "deathDate"):
        for s, d in sorted(values[prop]):
            if not d.strip():
                stats["empty"] += 1
                continue
            result = parse_date(d)
            if not result:
                stats["not parsed"] += 1
                unparsed.append(d)
                continue
            parsed[s][prop].append(result)
    for s in sorted(parsed):
        if death_before_birth(parsed[s]):
            stats["death before birth"] += sum(len(x) for x in parsed[s].values())
            continue
        for prop, results in parsed[s].items():
            target = prop + "Normalized"
            for value, uncertain in results:
                t.add((iri(s), IRI(JLO + target), value))
                if uncertain:
                    t.add((iri(s), IRI(JLO + prop.replace("Date", "DateUncertain")), Literal("true", XSD + "boolean")))
                    stats["uncertain"] += 1
                stats["normalised"] += 1
    examples = ", ".join(sorted(set(unparsed), key=lambda x: (len(x), x))[-8:])
    run.note(f"Dates: {dict(sorted(stats.items()))}. Examples of values left out: {examples}.")
    return t


def death_before_birth(parsed):
    """parsed: {"birthDate": [(literal, uncertain)], "deathDate": [...]}; compared by year, for records with one birth
    and one death date (records with several, e.g. in epidat, may stand for several people and keep them)."""
    births, deaths = parsed.get("birthDate", []), parsed.get("deathDate", [])
    if not (len(births) == 1 and len(deaths) == 1):
        return False
    death_hi, birth_lo = years_of(deaths[0][0])[1], years_of(births[0][0])[0]
    return death_hi is not None and birth_lo is not None and death_hi < birth_lo


# --- places ----------------------------------------------------------------------------------------

def place_key(s):
    """Texts compared in Unicode NFC (GND writes "Königsberg" decomposed, haskala composed), spaces collapsed, lower case."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s)).strip().lower()


def places(run, values, dictionaries):
    sources = [("pairs in the data", dictionaries["pairs"]), ("cm-entities-wikidata places", dictionaries["cm"]),
               ("rujen and geo-coordinates places", dictionaries["rujen_geo"])]
    t = set()
    stats = Counter()
    for prop, target in (("birthLocation", "birthLocationURI"), ("deathLocation", "deathLocationURI")):
        existing = values[target + "_subjects"]
        for s, label in sorted(values[prop]):
            if s in existing:
                stats["already linked"] += 1
                continue
            key = place_key(label)
            hit = None
            for name, dictionary in sources:
                found = dictionary.get(key) or (dictionary.get(key.split(",")[0].strip()) if "," in key else None)
                if found:
                    if len(found) == 1:
                        hit = (name, next(iter(found)))
                    break  # ambiguous in the best source: do not fall back to a weaker one
            if hit:
                t.add((iri(s), IRI(JLO + target), iri(hit[1])))
                stats[f"via {hit[0]}"] += 1
            else:
                stats["not linked"] += 1
    run.note(f"Places: {dict(sorted(stats.items()))}.")
    return t


# --- occupations -----------------------------------------------------------------------------------

def norm_occ(s):
    return re.sub(r"\s+", " ", s.replace("_", " ")).strip().lower()


def occupations(run, values):
    concepts = defaultdict(set)
    for o in values["occupation_iris"]:
        concepts[norm_occ(unquote(o.rsplit("/", 1)[-1]))].add(o)
    prop = JLO + ("occupationConcept" if run.params["legacy_terms"] else "occupationURI")
    t = set()
    matched = unmatched = 0
    for s, o in sorted(values["occupation_literals"]):
        hits = concepts.get(norm_occ(o))
        if hits and len(hits) == 1:
            t.add((iri(s), IRI(prop), iri(next(iter(hits)))))
            matched += 1
        else:
            unmatched += 1
    run.note(f"Occupations: {matched:,} text occupations matched to one of {len(values['occupation_iris']):,} "
             f"occupation IRIs, {unmatched:,} not matched.")
    if not run.params["legacy_terms"]:
        before = len(t)
        for s, o in values["occupation_iri_statements"]:
            t.add((iri(s), IRI(prop), iri(o)))
        run.note(f"Occupation IRIs stated with jl:occupation or jl:occpation: "
                 f"{len(values['occupation_iri_statements']):,}, as jl:occupationURI ({len(t) - before:,} new).")
    return t


def generate(run):
    v = defaultdict(set)
    record_ok = lambda s: not s.startswith(EP)
    for name in RECORDS:
        for s, p, o in run.triples(name):
            s = str(s)
            local = p[len(JLO):] if p.startswith(JLO) else None
            if local in ("birthDate", "deathDate", "birthLocation", "deathLocation"):
                if isinstance(o, Literal) and record_ok(s):
                    v[local].add((s, o.value))
            elif local in ("birthLocationURI", "deathLocationURI"):
                if record_ok(s):
                    v[local + "_subjects"].add(s)
                if local == "birthLocationURI" and record_ok(s):
                    v["birth_uri_pairs"].add((s, str(o)))
            if local in ("occupation", "occpation"):
                if isinstance(o, Literal):
                    if record_ok(s):
                        v["occupation_literals"].add((s, o.value))
                else:
                    v["occupation_iris"].add(str(o))
                    if record_ok(s):
                        v["occupation_iri_statements"].add((s, str(o)))
            if local == "occpation":
                v["occpation"].add((s, o))
            if local == "occupationURI" and not isinstance(o, Literal):
                v["occupation_iris"].add(str(o))   # occupation IRIs stated as such (bhr since 2026-10-12)
    # dictionaries of the places
    pairs = defaultdict(set)
    uri_of = defaultdict(set)
    for s, u in v["birth_uri_pairs"]:
        uri_of[s].add(u)
    for s, label in v["birthLocation"]:
        for u in uri_of.get(s, ()):
            pairs[place_key(label)].add(u)
    cm, cm_places, cm_labels = defaultdict(set), set(), defaultdict(set)
    for s, p, o in run.triples("cm_entities"):
        if p == RDF_TYPE and classes.kind(o) == "Place":
            cm_places.add(str(s))
        elif p == SKOS + "prefLabel" and isinstance(o, Literal) and o.lang in ("de", "en"):
            cm_labels[str(s)].add(o.value)
    for s in cm_places:
        for label in cm_labels[s]:
            cm[place_key(label)].add(s)
    rujen_geo = defaultdict(set)
    rujen_places, rujen_labels = set(), defaultdict(set)
    for s, p, o in run.triples("rujen"):
        if p == RDF_TYPE and classes.kind(o) == "Place":
            rujen_places.add(str(s))
        elif p == SKOS + "prefLabel" and isinstance(o, Literal):
            rujen_labels[str(s)].add(o.value)
    for s in rujen_places:
        for label in rujen_labels[s]:
            rujen_geo[place_key(label)].add(s)
    for s, p, o in run.triples("geo_coordinates"):
        if p == SKOS + "prefLabel" and isinstance(o, Literal):
            rujen_geo[place_key(o.value)].add(str(s))
    run.log(f"values: " + ", ".join(f"{k} {len(x):,}" for k, x in sorted(v.items())))
    run.write_turtle("records-normalized-dates.ttl.gz", dates(run, v))
    run.write_turtle("records-normalized-places.ttl.gz", places(run, v, {"pairs": pairs, "cm": cm, "rujen_geo": rujen_geo}))
    run.write_turtle("records-normalized-occupations.ttl.gz", occupations(run, v))
    if run.params["legacy_terms"]:
        run.write_turtle("records-normalized-occupation-fix.ttl.gz",
                         {(iri(s), IRI(JLO + "occupation"), o) for s, o in v["occpation"]})
