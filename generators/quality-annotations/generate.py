"""quality-annotations: problems in the data that adding facts cannot fix, as quality annotations.

A port of quality_annotations of kg-complements (datasets_algorithmic.py, 2026-10-06; decision 0020), keeping only
the annotations about the data (decided 2026-10-12): those about the state of the old catalogues and dumps are
fixed there or obsolete, those about legacy entity pages are not complements (0008). Each annotation is a
dqv:QualityAnnotation and oa:Annotation with its target, the problem as text (oa:bodyValue) and its kind
(dcterms:type); IRIs data/quality-annotations/annotation/<hash>, no creation date (the version says when).

Rule-based checks, run on the inputs:
- dates of the records that records-normalized leaves out (its date rules are shared code), on the record;
- issues of Compact Memory in a year more than 15 years away from every other year of their journal (the rule of
  date_review.tsv of the full-text bundle, there per page), on the issue, which states the date;
- per version: RDF-star statements, the misspelt property jl:occpation, IRIs as values of jl:occupation (range:
  text), dcterms:created as a plain string, jl:lat and jl:lon swapped against geo:asWKT;
- problems found by hand (FOUND), checked to be still in the input.
"""

import hashlib
import re
from collections import Counter, defaultdict

from jl import rdf
from jl.generator import GeneratorError, load_shared
from jl.rdf import IRI, RDF_TYPE, Literal
from jl.turtle import PREFIXES

rn = load_shared("records-normalized", "generate")

INPUTS = {**rn.RECORDS, "compact_memory": "compact-memory/2026-10-12", "geo_coordinates": "geo-coordinates/2018-08-08",
          "nrwbibdjg": "nrwbibdjg/2024-05-24"}
PARAMS = {}

JLO = PREFIXES["jl"]
DCT = PREFIXES["dcterms"]
DQV = PREFIXES["dqv"]
OA = PREFIXES["oa"]
RDFS = PREFIXES["rdfs"]
SKOS = PREFIXES["skos"]
GEO_WKT = "http://www.opengis.net/ont/geosparql#asWKT"
BASE = "http://data.judaicalink.org/data/quality-annotations/annotation/"
CM = "http://data.judaicalink.org/data/compact-memory/"
GAP = 15
HTML_VIEW = "https://data.judaicalink.org/data/html/"

# found by hand: (input, target, kind, text, a triple pattern (s, p) that must still be in the input)
FOUND = [
    ("compact_memory", CM + "3330981", "data error",
     "The title of this article in the page table of Compact Memory (compact-memory-supp, page 3331118) is several "
     "columns run together; the title is 'Niwa Polska [Rezension]'.", (CM + "3330981", RDF_TYPE)),
]


def version_iri(ref):
    slug, version = ref.split("/")[:2]
    return f"http://data.judaicalink.org/datasets/{slug}/{version}"


def generate(run):
    t = set()
    kinds = Counter()

    def note(target, kind, text):
        a = IRI(BASE + hashlib.sha1(f"{target}|{kind}|{text}".encode()).hexdigest()[:16])
        t.update({(a, IRI(RDF_TYPE), IRI(DQV + "QualityAnnotation")), (a, IRI(RDF_TYPE), IRI(OA + "Annotation")),
                  (a, IRI(OA + "hasTarget"), rn.iri(target)), (a, IRI(OA + "motivatedBy"), IRI(DQV + "qualityAssessment")),
                  (a, IRI(OA + "bodyValue"), Literal(text, lang="en")), (a, IRI(DCT + "type"), Literal(kind))})
        kinds[kind] += 1

    # --- the record datasets and the other versions: one pass each ---------------------------------
    dates = set()
    for name, ref in INPUTS.items():
        if name == "compact_memory":
            continue
        report = {}
        c = Counter()
        examples = {}
        lat, lon, wkt = {}, {}, defaultdict(set)
        for p in run.inputs(name):
            for s, pred, o in rdf.read_triples(p, report):
                local = pred[len(JLO):] if pred.startswith(JLO) else None
                if local in ("birthDate", "deathDate") and name in rn.RECORDS and isinstance(o, Literal) \
                        and not s.startswith(rn.EP) and o.value.strip():
                    dates.add((str(s), local, o.value))
                elif local == "occpation":
                    c["occpation"] += 1
                elif local == "occupation" and not isinstance(o, Literal):
                    c["occupation IRI"] += 1
                    examples.setdefault("occupation IRI", o)
                    if o.startswith(HTML_VIEW):
                        c["occupation HTML view"] += 1
                elif pred == DCT + "created" and isinstance(o, Literal) and o.datatype in (None, rdf.XSD_STRING) \
                        and not o.lang:
                    c["created"] += 1
                    examples.setdefault("created", o.value)
                elif local == "lat" and isinstance(o, Literal):
                    lat[s] = o.value
                elif local == "lon" and isinstance(o, Literal):
                    lon[s] = o.value
                elif pred == GEO_WKT and isinstance(o, Literal):
                    wkt[s].add(o.value)
        target = version_iri(ref)
        if report.get("rdf_star"):
            n = report["rdf_star"]
            note(target, "syntax", f"{n} statement{'s' if n > 1 else ''} of this version {'are' if n > 1 else 'is'} "
                 "RDF-star (a quoted triple << … >> as subject), which RDF 1.1 tools, QLever among them, reject; JudaicaLink's reader leaves "
                 "them out.")
        if c["occpation"]:
            note(target, "vocabulary", f"{c['occpation']:,} triples use the misspelt property jl:occpation instead of "
                 "jl:occupation; records-normalized states their occupation IRIs as jl:occupationURI.")
        if c["occupation IRI"]:
            note(target, "vocabulary", f"{c['occupation IRI']:,} values of jl:occupation are IRIs (e.g. "
                 f"<{examples['occupation IRI']}>), but its range is text; records-normalized states them as "
                 "jl:occupationURI." + (f" {c['occupation HTML view']:,} of them are addresses of HTML views "
                 f"({HTML_VIEW}…), not occupation IRIs." if c["occupation HTML view"] else ""))
        if c["created"]:
            note(target, "datatype", f"{c['created']:,} values of dcterms:created are plain strings (e.g. "
                 f"\"{examples['created']}\"), not typed as xsd:dateTime.")
        swapped = []
        for s in sorted(set(lat) & set(lon)):
            points = [m.groups() for w in wkt.get(s, ()) if (m := re.search(r"Point\s*\(\s*(\S+)\s+(\S+)\s*\)", w))]
            try:
                la, lo = float(lat[s]), float(lon[s])
                if points and all(abs(float(x) - la) < 0.01 and abs(float(y) - lo) < 0.01 and abs(la - lo) >= 0.01
                                  for x, y in points):
                    swapped.append(s)
            except ValueError:
                continue
        if swapped:
            s = swapped[0]
            note(target, "data error", f"jl:lat and jl:lon are swapped for {len(swapped):,} of {len(set(lat) & set(lon)):,} "
                 f"places: jl:lat holds the longitude of geo:asWKT (\"Point(longitude latitude)\"), jl:lon the "
                 f"latitude (e.g. <{s}>: jl:lat \"{lat[s]}\", jl:lon \"{lon[s]}\").")
        run.log(f"{name}: {dict(c)}, rdf_star {report.get('rdf_star', 0)}, swapped {len(swapped)}")

    # --- dates that records-normalized leaves out ------------------------------------------------------
    parsed = defaultdict(lambda: defaultdict(list))
    reasons = Counter()
    for s, prop, value in sorted(dates):
        result = rn.parse_date(value)
        if result:
            parsed[s][prop].append((value, result))
            continue
        why = rn.why_not(value)
        reasons[re.sub(r"the year \d+", "the year", re.split(r",| \(|:", why)[0]) if why else "no recognised form"] += 1
        note(s, "date", f"jl:{prop} '{value}' could not be normalised (records-normalized): "
             + (why or "not a date in a recognised form") + ".")
    for s in sorted(parsed):
        if rn.death_before_birth({p: [r for _, r in x] for p, x in parsed[s].items()}):
            values = "; ".join(f"jl:{p} '{v}'" for p in sorted(parsed[s]) for v, _ in parsed[s][p])
            note(s, "date", f"The death is before the birth ({values}), so records-normalized normalises neither "
                 "(a typo, or years before the common era written without a minus sign).")
            reasons["death before birth"] += 1
    run.note(f"Dates left out by records-normalized: {dict(sorted(reasons.items()))}.")

    # --- Compact Memory: issues in isolated years ----------------------------------------------------
    journal_of, date_of, issues, titles, present = {}, {}, set(), {}, set()
    for s, p, o in run.triples("compact_memory"):
        if p == JLO + "belongsToIssue":
            issues.add(str(o))
        elif p == JLO + "belongsToJournal":
            journal_of[str(s)] = str(o)
        elif p == DCT + "date" and isinstance(o, Literal):
            date_of[str(s)] = o.value
        elif p in (DCT + "title", RDFS + "label", SKOS + "prefLabel") and isinstance(o, Literal):
            titles.setdefault(str(s), {})[p] = o.value
        for f in FOUND:
            if f[0] == "compact_memory" and (str(s), str(p)) == f[4]:
                present.add(f[1])
    years = defaultdict(set)
    dated = {}
    for i in issues:
        m = re.match(r"(\d{4})", date_of.get(i, ""))
        if m and i in journal_of:
            dated[i] = int(m.group(1))
            years[journal_of[i]].add(dated[i])
    isolated = {j: {y for y in ys if len(ys) > 1 and all(o == y or abs(o - y) > GAP for o in ys)}
                for j, ys in years.items()}
    n = 0
    for i in sorted(dated):
        j = journal_of[i]
        if dated[i] in isolated[j]:
            title = next((titles.get(j, {}).get(p) for p in (DCT + "title", SKOS + "prefLabel", RDFS + "label")
                          if titles.get(j, {}).get(p)), j)
            note(i, "date", f"The year of this issue, {dated[i]} (dcterms:date \"{date_of[i]}\"), is more than {GAP} "
                 f"years away from every other year of the issues of '{title}'; probably a typo in the source "
                 "metadata.")
            n += 1
    run.note(f"Compact Memory: {n} issues in isolated years, of {len(dated):,} dated issues with pages.")

    for name, target, kind, text, _ in FOUND:
        if target not in present:
            raise GeneratorError(f"found by hand: {target} is no longer in {name}; check the annotation")
        note(target, kind, text)

    run.note(f"Annotations by kind: {dict(sorted(kinds.items()))}.")
    run.write_turtle("quality-annotations.ttl.gz", t)
