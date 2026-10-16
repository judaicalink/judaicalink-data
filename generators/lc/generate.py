"""lc: the records of the LC Name Authority File that JudaicaLink uses (decision 0029), made from the LC dump.

1. The selection list (lc-selection.tsv.gz): one row per LC identifier and reason, with the current identifier.
   - linked: every LC name identifier that a stable version of one of our datasets (and the run of gnd named in
     LINKED, through EntityFacts) links as object: the authority record (id.loc.gov/authorities/names/<id>) or its
     Real World Object (id.loc.gov/rwo/agents/<id>); the detail is the dataset.
   LC marks a withdrawn record as madsrdf:DeprecatedAuthority (record status "deprecated") and states no successor
   in the export (madsrdf:hasLaterEstablishedForm links a heading to a later, different one, e.g. a renamed
   conference, and is no replacement). So a cited deprecated identifier has no current identifier.
2. The data (lc.ttl.gz): every current record named by the list, read from the dump in one pass (blocks between
   "# BEGIN" and "# END"). Each record data/lc/<id> keeps the statements of the authority (subject replaced by the
   record IRI, IRIs in canonical form, jl.iris) and of its Real World Object (dates, places, occupations, fields of
   activity, languages; blank nodes of occupations and fields flattened to their IRI), and gets owl:sameAs
   <http://id.loc.gov/authorities/names/<id>>, the classes the entity pages know (foaf:Person for personal names,
   foaf:Organization for corporate names, jl:Place for geographic names, jl:Work for titles), skos:prefLabel
   (madsrdf:authoritativeLabel), skos:altLabel (the variant labels), jl:birthDate/deathDate (madsrdf:birthDate/
   deathDate), jl:birthLocation(URI)/deathLocation(URI), and owl:sameAs for the exact external authorities that are
   identifiers of a known source (GND, VIAF clusters, ISNI, Wikidata, TGN; not the VIAF source records
   viaf.org/en/viaf/LC|<id>, which are LC's own record in VIAF). Left out: the administrative metadata, sources and
   element lists (blank nodes), the affiliations (blank nodes), and links to JudaicaLink (decision 0029).
3. Deprecated identifiers our data cites: <http://id.loc.gov/authorities/names/<id>> owl:deprecated true.
"""

import csv
import gzip
import re
from collections import defaultdict

from jl import identifiers, iris
from jl.generator import GeneratorError, stable_inputs
from jl.iris import canonical
from jl.rdf import IRI, RDF_TYPE, XSD, BNode, Literal, parse_ntriples, unescape_string
from jl.turtle import PREFIXES

GND_RUN = "run-20261016T121839Z"   # the gnd run; becomes the gnd version once it is made
LINKED = stable_inputs("linked_", exclude={"lc", "gnd-persons", "gnd-persons-entityfacts", "ep", "compact-memory",
                                           "compact-memory-supp", "cm-ocr-quality", "cm-tagme", "corrections-links",
                                           "quality-annotations", "judaicalink-agents", "judaicalink-vocabulary",
                                           "ontology"},
                       add={"gnd": GND_RUN})
INPUTS = {"names": "inputs:lc/names-2026-09-27/names.madsrdf.nt.gz", **LINKED}
PARAMS = {}

JL = "http://data.judaicalink.org/data/"
NAMES = "http://id.loc.gov/authorities/names/"
RWO = "http://id.loc.gov/rwo/agents/"
MADS = "http://www.loc.gov/mads/rdf/v1#"
JLO, SKOS, OWL, FOAF, RDFS = (PREFIXES[p] for p in ("jl", "skos", "owl", "foaf", "rdfs"))
SAME = OWL + "sameAs"

LC_ID = r"[a-z]{1,3}[0-9]+"
# the LC identifier of an IRI in any of its forms: authority record or Real World Object (jl.identifiers knows only
# the record; see the README)
LC_IRI = re.compile(r"^https?://id\.loc\.gov/(?:authorities/names|rwo/agents)/(" + LC_ID + r")(?:\.html|\.rdf|\.json)?/?$")
BEGIN = re.compile(r"^# BEGIN /authorities/names/(" + LC_ID + r")\s*$")
LABEL_OF = re.compile(r'^<http://id\.loc\.gov/authorities/names/(' + LC_ID + r')> <http://www\.loc\.gov/mads/rdf/v1#'
                      r'authoritativeLabel> "((?:[^"\\]|\\.)*)"', re.M)

CLASSES = {"PersonalName": FOAF + "Person", "CorporateName": FOAF + "Organization", "Geographic": JLO + "Place",
           "HierarchicalGeographic": JLO + "Place", "Title": JLO + "Work", "NameTitle": JLO + "Work"}
LEFT_OUT = {MADS + "adminMetadata", MADS + "hasSource", MADS + "elementList", MADS + "componentList",
            MADS + "hasAffiliation", MADS + "identifiesRWO", MADS + "isIdentifiedByAuthority", RDFS + "label"}
FLATTEN = {MADS + "occupation", MADS + "fieldOfActivity"}   # RWO -> blank node -> IRI
KNOWN = {"gnd", "viaf", "isni", "wikidata", "tgn"}


def lc_id(term):
    m = LC_IRI.match(term) if isinstance(term, str) and not isinstance(term, BNode) else None
    return m.group(1) if m else None


def wikidata_page(x):
    """https://www.wikidata.org/wiki/Q<n> (the page of an item, as LC states it) as the item."""
    m = re.match(r"^https?://(?:www\.)?wikidata\.org/wiki/(Q[0-9]+)$", x)
    return f"http://www.wikidata.org/entity/{m.group(1)}" if m else x


def select(run):
    rows = set()
    for name, ref in LINKED.items():
        slug = ref.split("/", 1)[0]
        for _s, _p, o in run.triples(name):
            n = lc_id(o)
            if n:
                rows.add((n, "linked", slug))
    return rows


def blocks(path):
    """(id, lines) of each record of the dump."""
    current, lines = None, []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            if line.startswith("# BEGIN"):
                m = BEGIN.match(line)
                current, lines = (m.group(1) if m else None), []
            elif line.startswith("# END"):
                if current:
                    yield current, lines
                current = None
            elif current and line.strip():
                lines.append(line)


def generate(run):
    rows = select(run)
    wanted = {n for n, _r, _d in rows}
    run.log(f"listed {len(wanted):,} LC identifiers")
    kept, deprecated, names = {}, set(), {}
    for n, lines in blocks(run.input("names")):
        text = "".join(lines)
        if "#Geographic>" in text or "#HierarchicalGeographic>" in text:
            for m in LABEL_OF.finditer(text):
                names[m.group(1)] = unescape_string(m.group(2))
        if n in wanted:
            if MADS + "DeprecatedAuthority>" in text:
                deprecated.add(n)
            else:
                kept[n] = lines
    missing = sorted(wanted - set(kept) - deprecated)
    run.log(f"dump: {len(kept):,} records kept, {len(deprecated):,} cited identifiers deprecated, "
            f"{len(missing):,} not in the dump; {len(names):,} place names")
    for n in missing[:200]:
        run.log("unknown identifier:", n)

    t = set()
    for n in sorted(kept):
        rec = IRI(JL + "lc/" + n)
        auth, rwo = NAMES + n, RWO + n
        t.add((rec, IRI(SAME), IRI(NAMES + n)))
        triples = list(parse_ntriples(kept[n]))
        by_subject = defaultdict(list)
        for s, p, o in triples:
            by_subject[s].append((p, o))
        for s, p, o in triples:
            if s not in (auth, rwo) or p in LEFT_OUT:
                continue
            if p == MADS + "hasVariant":
                for vp, vo in by_subject.get(o, []):
                    if vp == MADS + "variantLabel" and isinstance(vo, Literal):
                        t.add((rec, IRI(SKOS + "altLabel"), Literal(vo.value, None, None)))
                continue
            if p in FLATTEN and isinstance(o, BNode):
                for vp, vo in by_subject.get(o, []):
                    if vp == p and isinstance(vo, str) and not isinstance(vo, (BNode, Literal)):
                        t.add((rec, IRI(p), IRI(canonical(vo))))
                continue
            if p in (MADS + "birthPlace", MADS + "deathPlace"):
                which = "birth" if p.endswith("birthPlace") else "death"
                if isinstance(o, BNode):
                    for vp, vo in by_subject.get(o, []):
                        if vp == RDFS + "label" and isinstance(vo, Literal):
                            t.add((rec, IRI(JLO + which + "Location"), Literal(vo.value)))
                elif isinstance(o, str) and not isinstance(o, Literal):
                    t.add((rec, IRI(p), IRI(canonical(o))))
                    t.add((rec, IRI(JLO + which + "LocationURI"), IRI(canonical(o))))
                    name = names.get(lc_id(o))
                    if name:
                        t.add((rec, IRI(JLO + which + "Location"), Literal(name)))
                continue
            if isinstance(o, BNode):
                continue
            if isinstance(o, str) and not isinstance(o, Literal):
                x = canonical(wikidata_page(o))
                if identifiers.is_ours(x):
                    continue   # links to JudaicaLink are never evidence (decision 0029)
                o = IRI(x)
                if p == MADS + "hasExactExternalAuthority" and iris.kind(x) in KNOWN:
                    t.add((rec, IRI(SAME), o))
            t.add((rec, IRI(p), o))
            if p == RDF_TYPE and o.startswith(MADS) and o[len(MADS):] in CLASSES:
                t.add((rec, IRI(RDF_TYPE), IRI(CLASSES[o[len(MADS):]])))
            elif p == MADS + "authoritativeLabel" and isinstance(o, Literal):
                t.add((rec, IRI(SKOS + "prefLabel"), Literal(o.value, None, o.lang)))
            elif p in (MADS + "birthDate", MADS + "deathDate") and isinstance(o, Literal):
                t.add((rec, IRI(JLO + ("birthDate" if p.endswith("birthDate") else "deathDate")), Literal(o.value)))
    for n in sorted(deprecated):
        t.add((IRI(NAMES + n), IRI(OWL + "deprecated"), Literal("true", XSD + "boolean")))

    with gzip.open(run.path("lc-selection.tsv.gz"), "wt", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["lc", "current", "reason", "detail"])
        for n, reason, detail in sorted(rows):
            w.writerow([n, n if n in kept else "", reason, detail])
    by_dataset = defaultdict(set)
    for n, _r, d in rows:
        by_dataset[d].add(n)
    run.note(f"{len(kept):,} records of {len(wanted):,} linked identifiers ("
             + ", ".join(f"{d} {len(v):,}" for d, v in sorted(by_dataset.items(), key=lambda x: -len(x[1])))
             + f"); {len(deprecated):,} cited identifiers deprecated; {len(missing):,} not in the dump.")
    if not kept:
        raise GeneratorError("no LC record found")
    run.write_turtle("lc.ttl.gz", t)
