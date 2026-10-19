"""ep: the entity pages, made from the previous version of ep and the records of all datasets (decision 0022).

1. Groups: the transitive closure of the identity links over the records (JudaicaLink resources of the core classes:
   persons, places, organisations, works, subjects, and the entities linked in Compact Memory), computed fresh in
   every run. Identity links: owl:sameAs, gndo:gndIdentifier (IRI or literal) and replacements by exactly one IRI
   (dcterms:isReplacedBy); every target is a key after normalisation (key()); the same key joins, different keys
   never prevent a join. Entity pages are never part of the closure. A JudaicaLink IRI that is no record (e.g. a legacy
   NLI URI, linked to its record by ls-nli-legacy) is a node of the closure, never a member of a page.
2. Comparison with the previous version (its pages and their records): a group that contains the records of exactly
   one old page keeps its IRI; of several old pages the oldest IRI (lowest number) is kept, the others get
   jl:mergedInto + jl:mergeDate; an old page whose records are now in several groups gets jl:splitInto (all parts) +
   jl:splitDate; an old page with no record left gets jl:retiredDate; a group without an old page gets a new number
   above the highest number of the previous version. An old member that is not in the closure stands for what it
   was replaced by or derived from (dcterms:isReplacedBy, prov:wasDerivedFrom: the conflated legacy NLI URIs).
3. Facts of a page: chosen from its records by the precedence of the datasets (PRECEDENCE) and languages (as in
   ep-2026-10-06, kg-complements/ep_generator.py).

Files: ep.ttl.gz (the pages), ep-history.ttl.gz (one statement per event for IRIs that are no longer pages; the
history of the previous version is copied unchanged). Checks: every IRI of the previous version is a page or in the
history; the previous history is contained in the new one; every dataset that contributes a record is in PRECEDENCE.
The date of the events is the date of the run (data, not a version id; 0018).
"""

import math
import re
import unicodedata
from collections import Counter, defaultdict
from urllib.parse import unquote

from jl import catalog, classes, identifiers
from jl.generator import GeneratorError, slug_of, stable_inputs
from jl.iris import canonical_triples, canonical_wkt
from jl.linksets import contradict
from jl.rdf import IRI, RDF_TYPE, XSD, Literal
from jl.turtle import PREFIXES

# Datasets in order of precedence for choosing facts (decision 0009, 0022): 1 GND; 2 libraries and bibliographies;
# 3 curated reference works and research databases; 4 general knowledge bases; 5 automatically derived or linked;
# 6 the other authority datasets (0029: their records are members of an entity, their facts come last).
PRECEDENCE = [
    "gnd",
    "nli-records", "ubffm-persons", "nrwbibdjg", "haskala",
    "yivo", "rujen", "rujen-translation", "bhr", "djh", "hhkeydocs", "jre", "epidat", "stolpersteine", "hirsch-family",
    "sosy", "gba", "footprints",
    "dbpedia", "cm-entities", "geo-coordinates",
    "interlinks", "2014links", "geo-enriched", "dbp-wiki-geo-linking", "records-normalized",
    "ls-nli-legacy", "ls-yivo-wikidata",
    "wikidata", "viaf", "lc", "geonames",
]
# authority datasets whose records join an entity but never make one on their own, give no altLabels and do not vote
# for the preferred name (they fill a language only where no other record has a name in it)
AUTHORITY_ONLY = {"wikidata", "viaf", "lc", "geonames"}
# The deletions of the correction datasets are applied to every input (0023); a correction version that also adds
# triples (corrections-links 2026-10-12 adds none) is declared here as an input like any other dataset.
# The stable versions of the catalogue for the datasets above and record-classes, and RUNS (runs of datasets that are
# not versions yet; a run of ep with RUNS cannot become a version).
RUNS = {}
STABLE = {slug_of(ref): ref.split("/", 1)[1]
          for ref in stable_inputs(add=RUNS).values()
          if slug_of(ref) in set(PRECEDENCE) | {"record-classes"} | set(RUNS)}
INPUTS = {"previous": "ep/" + catalog.Catalog().entries["ep"].stable,
          **{s.replace("-", "_"): f"{s}/{v}" for s, v in STABLE.items()}}
# identity: "all" follows every identity link of every dataset (0022); "linksets" only those of our linksets, the
# replacements and the authority namespaces (decision 0029). The run log always reports the joins that only links
# outside the linksets make (the linksets still to be made).
PARAMS = {"identity": "linksets"}   # decision 0029: identity only from our linksets
# the datasets whose identity links are our own decisions (catalogue kind "linkset")
LINKSETS = {"2014links", "interlinks", "dbp-wiki-geo-linking", "ls-nli-legacy", "ls-yivo-wikidata", "ls-gnd", "ls-lc",
            "ls-geonames", "ls-viaf", "ls-wikidata", "ls-dbpedia"}
DATASET_OF = {s.replace("-", "_"): s for s in STABLE}
RANK = {s: i for i, s in enumerate(PRECEDENCE)}
# datasets whose typed resources are records (the others only add facts or links to records)
NOT_SOURCES = {"records-normalized", "ls-nli-legacy", "rujen-translation"}
LANGUAGES = ["en", "de", "he"]

JL = "http://data.judaicalink.org/data/"
EPNS = JL + "ep/"
JLO, FOAF, SKOS, RDFS, OWL, DCT = (PREFIXES[p] for p in ("jl", "foaf", "skos", "rdfs", "owl", "dcterms"))
GEO = PREFIXES["geosparql"]   # asWKT, wktLiteral (GeoSPARQL; PREFIXES["geo"] is WGS84)
PROV = "http://www.w3.org/ns/prov#"
GNDO = "http://d-nb.info/standards/elementset/gnd#"       # older datasets
GNDO_S = "https://d-nb.info/standards/elementset/gnd#"    # the publisher's form (gnd)
DBO = "http://dbpedia.org/ontology/"
SAME, GNDID, REPLACED, DERIVED = OWL + "sameAs", GNDO + "gndIdentifier", DCT + "isReplacedBy", PROV + "wasDerivedFrom"
JLSAME = JLO + "sameAs"   # identity as JudaicaLink states it (linksets, entities; decision 0029)
HISTORY = {JLO + "mergedInto", JLO + "mergeDate", JLO + "splitInto", JLO + "splitDate", JLO + "retiredDate",
           DCT + "isReplacedBy"}   # dcterms:isReplacedBy: the merges of sets before 2026-10 (none in the legacy set)

CLASS_OF_TYPE = {FOAF + "Person": "Person", JLO + "Person": "Person", JLO + "Place": "Place", DBO + "Place": "Place",
                 GNDO + "PlaceOrGeographicName": "Place", FOAF + "Organization": "Organization",
                 GNDO + "Work": "Work", JLO + "Work": "Work", GNDO_S + "Work": "Work",
                 GNDO_S + "PlaceOrGeographicName": "Place", SKOS + "Concept": "Subject", JLO + "Subject": "Subject",
                 classes.PLACE: "Place", classes.WORK: "Work"}   # the deprecated jl: classes read as before
# the key of an identifier of a source (jl.identifiers) in the closure
ID_KEY = {"gnd": "gnd:", "viaf": "viaf:", "wikidata": "wd:", "lc-names": "lc:", "geonames": "geonames:",
          "isni": "isni:", "tgn": "tgn:", "wikipedia-en": "wp-en:", "wikipedia-de": "wp-de:"}
# the keys of the authority datasets (decision 0029) and the namespaces of their records
AUTHORITY_KEYS = {"gnd": "GND", "lc": "LC", "geonames": "GeoNames", "wd": "Wikidata", "viaf": "VIAF"}
AUTHORITY_NS = {"gnd": "gnd/", "lc": "lc/", "geonames": "geonames/", "wd": "wikidata/", "viaf": "viaf/"}
SUBJECT_DATASETS = {"yivo", "djh", "rujen"}   # their other skos:Concepts are subjects (0022)
# datasets that state the classes of records of other datasets (0025): a class counts for the dataset whose namespace
# the record is in
CLASS_DATASETS = {"record-classes"}
CLASS_ORDER = ["Person", "Place", "Organization", "Work", "Subject"]
CLASS_IRI = {"Person": classes.PERSON, "Place": classes.PLACE, "Organization": classes.ORGANISATION,
             "Work": classes.WORK, "Subject": classes.SUBJECT}

FACT_PROPS = {
    SKOS + "prefLabel": "label", FOAF + "name": "label", RDFS + "label": "label",
    "http://purl.org/dc/elements/1.1/title": "label", DCT + "title": "label", SKOS + "altLabel": "alt",
    JLO + "birthDate": "birth", JLO + "deathDate": "death",
    JLO + "birthDateNormalized": "birthN", JLO + "deathDateNormalized": "deathN",
    JLO + "birthLocation": "birthPlace", JLO + "deathLocation": "deathPlace",
    JLO + "birthLocationURI": "birthPlaceURI", JLO + "deathLocationURI": "deathPlaceURI",
    JLO + "burialLocation": "burialPlace", JLO + "burialLocationURI": "burialPlaceURI",
    JLO + "occupation": "occupation", JLO + "occpation": "occupation", JLO + "occupationURI": "occupationURI",
    JLO + "hasAbstract": "abstract", JLO + "describedAt": "describedAt", GEO + "asWKT": "wkt",
    JLO + "lat": "lat", "http://www.w3.org/2003/01/geo/wgs84_pos#lat": "lat",
    JLO + "lon": "lon", "http://www.w3.org/2003/01/geo/wgs84_pos#long": "lon",
    SAME: "sameAs", GNDID: "gndId", GNDO_S + "gndIdentifier": "gndId",
    # for choosing the primary record of a dataset (record_order)
    GNDO + "succeedingPlaceOrGeographicName": "successor", GNDO_S + "succeedingPlaceOrGeographicName": "successor",
    GNDO + "succeedingCorporateBody": "successor", GNDO_S + "succeedingCorporateBody": "successor",
    GNDO + "realIdentity": "realIdentity", GNDO_S + "realIdentity": "realIdentity",
    "https://www.geonames.org/ontology#featureCode": "featureCode",
    "http://www.geonames.org/ontology#featureCode": "featureCode",
}
# Records known to be different entities, each joined once by wrong links that corrections-links deletes (decision
# 0023): a test, not a rule. If one of these pairs is in one group again, a new link joins them; the run stops so that
# it is corrected in the data, not here.
KNOWN_DISTINCT = [(JL + a, JL + b) for a, b in [
    ("dbpedia/Simeon_ben_Gamliel_II", "gnd/124813631"), ("dbpedia/Menahem_ben_Moshe_Bavli", "gnd/122534107"),
    ("dbpedia/Abraham_ben_David", "dbpedia/Abraham_ibn_Daud"), ("gnd/119169053", "gnd/143229036"),
    ("bhr/Kohn_Samuel", "gnd/137101554"), ("bhr/Kohn_Samuel-1", "bhr/Kohn_Samuel"),
    ("dbpedia/Herbert_Morrison", "gnd/11878501X"), ("dbpedia/Johann_Eck", "gnd/11852870X"),
    ("dbpedia/Randolph_Churchill", "gnd/119410346"), ("gnd/118960881", "gnd/1053284543"),
    ("gnd/1029068879", "gnd/13366936X"), ("gnd/119017806", "gnd/12279916X"), ("Granada", "dbpedia/Grenada"),
    ("nli/record/viaf-294403101", "gnd/118540238"), ("nli/record/viaf-179642103", "nli/record/viaf-22144877"),
    ("gnd/1140070320", "gnd/124269214"),
    ("hhkeydocs/person/gnd/117565725", "nli/record/viaf-112658460"),   # in 2025-03-21 hhkeydocs/Otto_Warburg
    ("hhkeydocs/person/gnd/117402362", "nli/record/viaf-59920664"),    # in 2025-03-21 hhkeydocs/Kurt_Singer
    ("dbpedia/Isaak_ben_Salomo_Sahula", "nli/record/viaf-308556423"),
    ("gnd/141432381", "nli/record/viaf-56213280"), ("Lubin", "rujen/lyubin"), ("Marseille", "rujen/marselj"),
    ("dbpedia/Berlin", "rujen/berlin"), ("Lemberg", "rujen/ljvov"),
]]
_IRI_BAD = re.compile(r'[<>"{}|^`\\\s]')


def iri(value):
    return IRI(_IRI_BAD.sub(lambda m: "%{:02X}".format(ord(m.group(0))), value))


def lit(value, dt=None, lang=None):
    return Literal(str(value), dt, lang)


# --- keys (0022) ---------------------------------------------------------------------------------------

def key(o):
    """The key of an identity target; None if it is not one (an entity page, an identifier without its syntax)."""
    o = o.strip()
    if o.startswith(EPNS) or o.startswith("https://data.judaicalink.org/data/ep/"):
        return None
    if o.startswith("https://data.judaicalink.org/"):
        o = "http://" + o[len("https://"):]
    m = re.match(r"^https?://d-nb\.info/gnd/([0-9]+[0-9X-]*)(/about)?/?$", o, re.I) or re.match(re.escape(JL) + r"gnd/([0-9]+[0-9X-]*)$", o)
    if m:
        return "gnd:" + m.group(1).upper()
    if re.match(r"^https?://d-nb\.info/gnd/", o):
        return None   # an empty or malformed GND number
    m = re.match(r"^https?://(?:www\.)?viaf\.org/viaf/(?:https?://viaf\.org/viaf/)?([0-9]+)/?$", o)
    if m:
        return "viaf:" + m.group(1)
    m = re.match(r"^https?://(?:www\.)?isni\.org/(?:isni/)?([0-9X \-]+)/?$", o)
    if m:
        n = re.sub(r"[ \-]", "", m.group(1))
        return "isni:" + n if len(n) == 16 else None
    m = re.match(r"^https?://id\.loc\.gov/(?:authorities/(?:names/)?|rwo/agents/)(n[a-z]?[0-9]+)\W*$", o)
    if m:
        return "lc:" + m.group(1)
    m = re.match(r"^https?://(?:www\.)?wikidata\.org/entity/(Q[0-9]+)$", o)
    if m:
        return "wd:" + m.group(1)
    m = re.match(r"^https?://(?:sws\.|www\.)?geonames\.org/([0-9]+)/?$", o) or re.match(re.escape(JL) + r"geonames/([0-9]+)$", o)
    if m:
        return "geonames:" + m.group(1)
    for prefix, ns in (("lc:", "lc/"), ("wd:", "wikidata/"), ("viaf:", "viaf/")):   # our authority records (0029)
        if o.startswith(JL + ns) and re.fullmatch(r"[A-Za-z]*[0-9]+", o[len(JL + ns):]):
            return prefix + o[len(JL + ns):]
    x = identifiers.identify(o)
    if x and x[0] in ("wikipedia-en", "wikipedia-de"):   # article and DBpedia resource: one key per language (0031)
        return ID_KEY[x[0]] + x[1]
    m = re.match(r"^https?://([a-z]+)\.dbpedia\.org/resource/(.+)$", o)
    if m:
        return f"dbpedia-{m.group(1)}:" + m.group(2)
    m = re.match(r"^https?://([a-z]+)\.wikipedia\.org/wiki/(.+)$", o)
    if m:
        return f"wp-{m.group(1)}:" + m.group(2)
    if o.startswith(JL):
        return o   # another JudaicaLink resource: the node itself
    if re.match(r"^https?://[^/#]+/[^#]", o):   # not an IRI without a path (http://data.bnf.fr/#foaf:Person)
        return "iri:" + re.sub(r"^https://", "http://", o.rstrip("/"))
    return None


class Closure:
    """Union-find over records and identifier keys. With owner (record -> the record dataset it counts for, or None),
    a union that would bring two records of the same record dataset into one group is refused (decision 0032) and
    noted in refused."""

    def __init__(self, owner=None):
        self.parent = {}
        self.owner = owner
        self.members = {}   # root -> {dataset: record} of the constrained datasets
        self.refused = []

    def find(self, x):
        p = self.parent
        p.setdefault(x, x)
        r = x
        while p[r] != r:
            r = p[r]
        while p[x] != r:
            p[x], x = r, p[x]
        return r

    def union(self, a, b, why=None):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return True
        if self.owner is not None:
            ma, mb = self.members_of(ra), self.members_of(rb)
            clash = sorted(d for d in ma.keys() & mb.keys() if ma[d] != mb[d])
            if clash:
                self.refused.append((a, b, why, clash[0], ma[clash[0]], mb[clash[0]]))
                return False
        if rb < ra:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.owner is not None:
            merged = {**self.members.pop(rb, {}), **self.members.get(ra, {})}
            self.members[ra] = merged
        return True

    def members_of(self, root):
        if root not in self.members:
            d = self.owner(root) if root in self.parent and self.parent[root] == root else None
            self.members[root] = {d: root} if d else {}
        return self.members[root]


# --- choosing facts (from kg-complements/ep_generator.py) ------------------------------------------------

def lang_rank(lang):
    return LANGUAGES.index(lang) if lang in LANGUAGES else (len(LANGUAGES) if not lang else len(LANGUAGES) + 1)


def src_rank(slug):
    return RANK.get(slug, len(RANK))


def norm_label(s):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s).strip())


def label_key(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().replace(",", " ").strip() or s.lower()


def choose_label(labels, gnd_labels):
    """The GND form if there is one; otherwise the most common form across the records (each record counts once per
    form), ties by language, then dataset precedence."""
    if gnd_labels:
        return sorted(gnd_labels, key=lambda v: (src_rank(v[2]), v[0]))[0][0]
    if not labels:
        return None
    count = set()
    spellings = defaultdict(Counter)
    best_of = {}
    for value, lang, ds, _t, rec in labels:
        k = label_key(value)
        if (k, value, rec) not in count:
            count.add((k, value, rec))
            spellings[k][value] += 1
        r = (lang_rank(lang), src_rank(ds))
        best_of[(k, value)] = min(best_of.get((k, value), r), r)
    votes = {k: len({rec for (kk, _v, rec) in count if kk == k}) for k in spellings}

    def spelling(k):
        return sorted(spellings[k], key=lambda v: (-spellings[k][v], v.isupper(), best_of[(k, v)], v))[0]

    def order(k):
        v = spelling(k)
        return (-votes[k], best_of[(k, v)], v)
    return spelling(sorted(votes, key=order)[0])


# GeoNames feature codes: a populated place before an administrative unit, and among populated places by rank
PLACE_CODES = ["P.PPLC", "P.PPLA", "P.PPLA2", "P.PPLA3", "P.PPLA4", "P.PPLA5", "P.PPL"]
KEY_IRI = {"gnd": "https://d-nb.info/gnd/{}", "lc": "http://id.loc.gov/authorities/names/{}",
           "geonames": "https://sws.geonames.org/{}/", "wd": "http://www.wikidata.org/entity/{}",
           "viaf": "https://viaf.org/viaf/{}"}


def id_order(r):
    """The identifier of a record, for the last tie: numbers by value, then the text."""
    tail = r.rstrip("/").rsplit("/", 1)[-1]
    digits = re.sub(r"\D", "", tail)
    return (int(digits) if digits else float("inf"), tail)


def record_order(members, facts, classes, named_by):
    """The order of the records of a group by which their facts are chosen (decision 0029): dataset precedence; then,
    among records of one dataset: not succeeded by another record of the group (the GND's succession of places and
    organisations: Vilnius before Wilna), not a pseudonym of one (gndo:realIdentity), a populated place before an
    administrative unit (GeoNames feature class P before A, PPLC before PPLA … PPL), named by more of our datasets,
    the lowest identifier. Returns {record: sort key} and {record: why it is first among its dataset}."""
    keys = {key(m) for m in members}
    order = {}
    for m in members:
        f = facts[m]
        succeeded = any(key(v) in keys for v, *_ in f.get("successor", []))
        pseudonym = any(key(v) in keys for v, *_ in f.get("realIdentity", []))
        codes = [str(v).rsplit("#", 1)[-1] for v, *_ in f.get("featureCode", [])]
        code = min((PLACE_CODES.index(c) if c in PLACE_CODES else len(PLACE_CODES) + (0 if c.startswith("P.") else 1)
                    for c in codes), default=len(PLACE_CODES) + 2)
        ds_rank = min(src_rank(ds) for ds in classes[m]) if classes[m] else len(RANK)
        order[m] = (ds_rank, succeeded, pseudonym, code, -len(named_by.get(key(m), ())), id_order(m))
    return order


def wkt_of(facts, rank_of):
    """geo:asWKT of the first record; else jl:lat/jl:lon as given."""
    if facts.get("wkt"):
        return sorted(facts["wkt"], key=lambda v: (rank_of(v), lang_rank(v[1]), v[0]))[0][0]
    lats = {ds: v for v, _l, ds, _t, _s in facts.get("lat", [])}
    lons = {ds: v for v, _l, ds, _t, _s in facts.get("lon", [])}
    for ds in sorted(set(lats) & set(lons), key=src_rank):
        try:
            return f"POINT({float(lons[ds])} {float(lats[ds])})"
        except ValueError:
            continue
    return None


def number(e):
    m = re.match(rf"^{re.escape(EPNS)}(\d+)$", e)
    return int(m.group(1)) if m else None


# --- identity ----------------------------------------------------------------------------------------------

# the order in which identity links are applied (the most trusted first, decision 0032): a link refused because of
# the one-record-per-dataset rule is then always a less trusted one
KEY_ORDER = {"gnd": 0, "lc": 1, "wd": 2, "viaf": 3, "wp-en": 4, "wp-de": 4, "geonames": 5, "isni": 6, "tgn": 6}


def closure(records, links, replaced, owner=None):
    """The groups: first every record in an authority namespace with its identifier (data/gnd/N is gnd:N), then the
    replacements (replaced by exactly one IRI: the same thing, a node, not a member), then the identity links in
    KEY_ORDER; with owner, unions against the one-record-per-dataset rule are refused (Closure)."""
    cl = Closure(owner)
    for r in sorted(records):
        cl.find(r)
    for r in sorted(records):
        k = key(r)
        if k and not k.startswith(JL) and re.match(r"(gnd|geonames|lc|wd|viaf|wp-en|wp-de):", k):
            cl.union(r, k, "own identifier")
    for s, ts in sorted(replaced.items()):
        if len(ts) == 1 and s not in records:
            cl.union(s, next(iter(ts)), "replaced")
    for s, k, *_ in sorted(links, key=lambda x: (KEY_ORDER.get(key_type(x[1]), 9), x[1], x[0])):
        cl.union(s, k, k)
    return cl


def key_type(k):
    return "jl" if k.startswith(JL) else k.split(":", 1)[0]


def owner(r):
    return r[len(JL):].split("/")[0] if r.startswith(JL) else "?"


def identity_report(run, records, classes, links, replaced, cl_all, cl_ours):
    """The joins that only identity links outside our linksets make (decision 0029): the groups of all links that
    the linksets alone would split, and per dataset and key the links that do such a join, with the datasets on the
    other side. Written to the run log ("identity report: ..."); the closure used is chosen by the parameter."""
    comp = {r: cl_ours.find(r) for r in records}
    parts = defaultdict(set)
    for r in records:
        parts[cl_all.find(r)].add(comp[r])
    split = {g: ps for g, ps in parts.items() if len(ps) > 1}
    in_split = sum(1 for r in records if cl_all.find(r) in split)
    run.log(f"identity report: {len(parts):,} groups with all links; {len(split):,} of them ({in_split:,} records) "
            f"would be split into {sum(len(p) for p in split.values()):,} groups by the linksets alone")
    by_key = defaultdict(list)   # key -> [(subject, dataset)]
    for s, k, ds, ours in links:
        by_key[k].append((s, ds if not ours else "+" + ds))
    needed = Counter()               # (dataset, key type) -> links doing a join the linksets do not make
    partners = defaultdict(Counter)  # (dataset, key type) -> datasets of the records joined on the other side
    examples = defaultdict(list)
    for k, subs in sorted(by_key.items()):
        members = {s for s, _ds in subs if s in comp}
        if k in comp:
            members.add(k)   # the key is itself a record (another JudaicaLink record)
        comps = {comp[m] for m in members}
        if len(comps) < 2:
            continue
        for s, ds in subs:
            if ds.startswith("+") or s not in comp:   # a link of ours
                continue
            others = {m for m in members if comp[m] != comp[s]}
            if not others:
                continue
            t = (ds, key_type(k))
            needed[t] += 1
            for m in others:
                partners[t][next(iter(sorted(classes[m]))) if classes.get(m) else owner(m)] += 1
            if len(examples[t]) < 3:
                examples[t].append(f"{s[len(JL):]} ~{k}~ {sorted(others)[0][len(JL):]}")
    for (ds, kt), n in sorted(needed.items(), key=lambda x: (-x[1], x[0])):
        other = ", ".join(f"{d} {c:,}" for d, c in partners[(ds, kt)].most_common())
        run.log(f"identity report: {ds} via {kt}: {n:,} links join records only linked this way; "
                f"other side: {other}; e.g. {' | '.join(examples[(ds, kt)])}")
    # the key types added one after the other (most needed first): how many groups would still be split
    order = Counter()
    for (_ds, kt), n in needed.items():
        order[kt] += n
    taken = set()
    for kt, _n in order.most_common():
        taken.add(kt)
        cl = closure(records, [x for x in links if x[3] or key_type(x[1]) in taken], replaced)
        left = defaultdict(set)
        for r in records:
            left[cl_all.find(r)].add(cl.find(r))
        n_split = sum(1 for ps in left.values() if len(ps) > 1)
        n_rec = sum(len(ps) for ps in left.values() if len(ps) > 1)
        run.log(f"identity report: with linksets for {', '.join(sorted(taken))}: {n_split:,} groups still split "
                f"(into {n_rec:,} parts)")


# --- the run -----------------------------------------------------------------------------------------------

def read_previous(run):
    """The previous version: its pages with their JudaicaLink members, its history statements, all its IRIs."""
    members, history, iris = defaultdict(set), set(), set()
    for s, p, o in run.triples("previous"):
        s = str(s)
        if not s.startswith(EPNS):
            continue
        iris.add(s)
        if p in HISTORY:
            history.add((IRI(s), IRI(p), o))
        elif p in (SAME, JLO + "represents", JLSAME) and isinstance(o, str) and o.startswith(JL) and not o.startswith(EPNS):
            members[s].add(str(o))
    inactive = {str(s) for s, _p, _o in history}
    pages = {e: members.get(e, set()) for e in iris if e not in inactive}   # pages without JudaicaLink members too
    return pages, history, iris


def generate(run):
    day = re.match(r"run-(\d{4})(\d{2})(\d{2})", run.id)
    day = f"{day.group(1)}-{day.group(2)}-{day.group(3)}"
    stats = Counter()
    prev_pages, prev_history, prev_iris = read_previous(run)
    stats["previous IRIs"] = len(prev_iris)
    stats["previous pages"] = len(prev_pages)

    # 1. read the datasets: types, identity links, replacements, facts
    classes = defaultdict(dict)        # record -> dataset -> {classes}
    links = []                         # (subject, key, dataset)
    replaced = defaultdict(set)        # IRI -> what it was replaced by (identity, if exactly one IRI)
    derived = defaultdict(set)         # IRI -> what it was derived from (only for the comparison, never identity)
    facts = defaultdict(lambda: defaultdict(list))
    entities_cm = set()
    replaced_key = {}                  # authority key -> the key it is replaced by (in the source's own IRIs)
    identity_props = {slug: {IRI(p) for p in identifiers.declared(slug)} | {
        IRI(p.replace("https://d-nb.info/", "http://d-nb.info/")) for p in identifiers.declared(slug)}
        for slug in DATASET_OF.values()}
    for name, slug in DATASET_OF.items():
        for s, p, o in run.triples(name):
            if p == REPLACED and not s.startswith(JL) and isinstance(o, str) and not isinstance(o, Literal):
                ks, ko = key(str(s)), key(str(o))
                if ks and ko and ks.split(":", 1)[0] in AUTHORITY_NS and ks != ko:
                    replaced_key[ks] = ko
                continue
            if not s.startswith(JL) or s.startswith(EPNS):
                continue
            s = str(s)
            if p == RDF_TYPE:
                c = CLASS_OF_TYPE.get(o)
                owner = slug
                if slug in CLASS_DATASETS:
                    owner = s[len(JL):].split("/")[0]
                    if owner not in STABLE:
                        raise GeneratorError(f"{slug}: a class for {s}, which is in no dataset namespace")
                if o == SKOS + "Concept" and owner not in SUBJECT_DATASETS:
                    c = None
                if c and owner not in NOT_SOURCES and slug not in LINKSETS:   # a linkset makes no records
                    classes[s].setdefault(owner, set()).add(c)
                continue
            if p == JLO + "entity" and slug == "cm-entities":
                entities_cm.add(str(o))
                continue
            x = identifiers.source_of(o, p) if p in identity_props.get(slug, ()) else None
            if x and identifiers.joins(slug, p, x[0]):   # declared, quality not below the threshold (0032)
                k = ID_KEY[x[0]] + x[1] if x[0] in ID_KEY else key(str(o))
                if k:
                    links.append((s, k, slug, p == JLSAME or slug in LINKSETS))
            elif p in (REPLACED, DERIVED) and isinstance(o, str) and o.startswith(JL) and not o.startswith(EPNS):
                (replaced if p == REPLACED else derived)[s].add(str(o))
            field = FACT_PROPS.get(p)
            if field:
                if isinstance(o, Literal):
                    facts[s][field].append((o.value, (o.lang or "").lower(), slug, "literal", s))
                else:
                    facts[s][field].append((str(o), "", slug, "uri", s))
    for e in entities_cm:   # the entities linked in Compact Memory are records (of cm-entities)
        classes[e].setdefault("cm-entities", set())
    records = {r for r in classes if r not in replaced}   # a replaced IRI is never a member (0032)
    stats["typed IRIs that are replaced (not members)"] = len(classes) - len(records)
    missing = sorted({d for r in records for d in classes[r]} - set(PRECEDENCE))
    if missing:
        raise GeneratorError(f"datasets with records but not in PRECEDENCE: {missing}")
    stats["records"] = len(records)

    # 2. the closure
    if run.params["identity"] not in ("all", "linksets"):
        raise GeneratorError(f"identity must be 'all' or 'linksets', not {run.params['identity']!r}")
    for ks, ko in replaced_key.items():   # a replaced identifier is the same thing as its successor (0029)
        replaced[ks].add(ko)
    several = {slug for slug in DATASET_OF.values() if (catalog.Catalog().get(slug) or {}) and
               catalog.Catalog().get(slug).data.get("several_per_entity")}

    def owner(r):
        """The record dataset a record counts for in the one-record-per-dataset rule (0032), or None: authority
        datasets (their duplicates are accepted) and datasets declared with several records per entity are free;
        dbpedia counts per language."""
        ds = sorted((d for d in classes.get(r, {}) if d not in CLASS_DATASETS), key=src_rank)
        d = ds[0] if ds else None
        if d is None or d in AUTHORITY_ONLY or d == "gnd" or d in several:
            return None
        return f"dbpedia/{r[len(JL):].split('/')[1]}" if d == "dbpedia" else d

    cl_all = closure(records, links, replaced, owner)
    cl_ours = closure(records, [x for x in links if x[3]], replaced, owner)
    identity_report(run, records, classes, links, replaced, cl_all, cl_ours)
    cl = cl_all if run.params["identity"] == "all" else cl_ours
    for a, b, why, ds, ra, rb in cl.refused:   # one record per record dataset (0032)
        stats["links refused (a second record of one dataset)"] += 1
        run.log(f"refused: {a} ~{why}~ {b}: would join {ra} and {rb} of {ds}")
    groups = defaultdict(set)
    for r in records:
        groups[cl.find(r)].add(r)
    for root in [g for g, ms in groups.items() if all(classes[m] and set(classes[m]) <= AUTHORITY_ONLY for m in ms)]:
        del groups[root]   # only records of authority datasets (e.g. a cluster whose link ls-viaf left out)
        stats["groups of authority records only (no page)"] += 1
    stats["groups"] = len(groups)
    joined = [(a, b) for a, b in KNOWN_DISTINCT if a in cl.parent and b in cl.parent and cl.find(a) == cl.find(b)]
    if joined:
        raise GeneratorError(f"records known to be different are in one group again (a new link joins them): {joined}")

    # 3. comparison with the previous pages
    def resolve(m, depth=0):
        """The groups an old member stands for."""
        if m in cl.parent and cl.find(m) in groups:
            return {cl.find(m)}
        if depth < 3 and (m in replaced or m in derived):
            return set().union(*(resolve(x, depth + 1) for x in sorted(replaced.get(m, set()) | derived.get(m, set()))))
        return set()
    targets = {e: set().union(*(resolve(m) for m in sorted(ms))) for e, ms in prev_pages.items()}
    split = {e for e, t in targets.items() if len(t) > 1}
    retired = {e for e, t in targets.items() if not t}
    candidates = defaultdict(list)
    for e, t in targets.items():
        if len(t) == 1:
            candidates[next(iter(t))].append(e)
    highest = max([number(e) or 0 for e in prev_iris])
    next_id = highest + 1
    iri_of, merged = {}, {}
    for root in sorted(groups, key=lambda g: min(groups[g])):
        olds = sorted(candidates.get(root, []), key=lambda e: (number(e) is None, number(e) or 0, e))
        if olds:
            iri_of[root] = olds[0]
            for e in olds[1:]:
                merged[e] = olds[0]
            stats["kept IRI"] += 1
        else:
            iri_of[root] = f"{EPNS}{next_id}"
            next_id += 1
            stats["new IRI"] += 1
    stats["merged"], stats["split"], stats["retired"] = len(merged), len(split), len(retired)
    stats["highest number"] = next_id - 1

    # 4. the history
    history = set(prev_history)
    d = lit(day, XSD + "date")
    for e, target in sorted(merged.items()):
        history |= {(IRI(e), IRI(JLO + "mergedInto"), IRI(target)), (IRI(e), IRI(JLO + "mergeDate"), d)}
    split_report = []
    for e in sorted(split):
        parts = sorted(iri_of[g] for g in targets[e])
        history |= {(IRI(e), IRI(JLO + "splitInto"), IRI(p)) for p in parts}
        history.add((IRI(e), IRI(JLO + "splitDate"), d))
        split_report.append((e, parts))
    for e in sorted(retired):
        history.add((IRI(e), IRI(JLO + "retiredDate"), d))
    pages = set(iri_of.values())
    in_history = {str(s) for s, _p, _o in history}
    unaccounted = sorted(e for e in prev_iris if e not in pages and e not in in_history)
    if unaccounted:
        raise GeneratorError(f"{len(unaccounted)} IRIs of the previous version are neither pages nor in the history, "
                             f"e.g. {unaccounted[:3]}")

    # 5. the pages
    def current_key(k):   # the identifier an authority dataset of our inputs replaced it by (dcterms:isReplacedBy)
        prefix, _, ident = k.partition(":")
        if prefix not in AUTHORITY_NS:
            return k
        node, seen = JL + AUTHORITY_NS[prefix] + ident, set()
        while node not in seen:
            seen.add(node)
            if len(replaced.get(node, ())) == 1:
                node = next(iter(replaced[node]))
            elif key(node) in replaced_key:
                prefix, _, ident = replaced_key[key(node)].partition(":")
                node = JL + AUTHORITY_NS[prefix] + ident
            else:
                break
        return key(node) or k

    def current_iri(v):
        k = key(v)
        c = current_key(k) if k else None
        if c and c != k:
            prefix, _, ident = c.partition(":")
            return iri(KEY_IRI[prefix].format(ident))
        return iri(v)

    named_by = defaultdict(set)   # key -> the datasets that name it
    for _s, k, ds, *_ in links:
        named_by[k].add(ds)
    out = set()
    by_class = Counter()
    for root in sorted(groups, key=lambda g: iri_of[g]):
        page = IRI(iri_of[root])
        members = sorted(groups[root])
        merged_facts = defaultdict(list)
        for m in members:
            for field, vals in facts[m].items():
                merged_facts[field].extend(vals)
        datasets = {ds for m in members for ds in classes[m]}
        cls = {c for m in members for cs in classes[m].values() for c in cs}
        if not cls:
            cls.add("Person" if merged_facts.get("birth") or merged_facts.get("death") else "Subject")
        c = next(x for x in CLASS_ORDER if x in cls)
        by_class[c] += 1
        out.add((page, IRI(RDF_TYPE), IRI(CLASS_IRI[c])))   # the class of what it is (jl:EntityPage deprecated)
        rank = record_order(members, facts, classes, named_by)
        last = (len(RANK) + 1,)
        rank_of = lambda v: rank.get(v[4], last)

        # names
        all_labels = [(norm_label(v), lang, ds, None, s) for v, lang, ds, t, s in merged_facts.get("label", [])
                      if t == "literal"]
        labels = [x for x in all_labels if x[2] not in AUTHORITY_ONLY]
        gnd = sorted((x for x in labels if x[2] == "gnd"), key=lambda x: (rank_of(x), x[0]))
        if not labels:
            labels = all_labels or [(unquote(m.rstrip("/").rsplit("/", 1)[-1]).replace("_", " "), "", "cm-entities",
                                     None, m) for m in members]
        pref = choose_label(labels, gnd)
        seen = set()
        if pref:
            out.add((page, IRI(SKOS + "prefLabel"), lit(pref)))
            seen.add(label_key(pref))
        for lang in LANGUAGES:
            cands = [v for v in labels if v[1] == lang] or [v for v in all_labels if v[1] == lang]
            if cands:
                v = sorted(cands, key=lambda x: (x[0].isupper(), rank_of(x), x[0]))[0]
                out.add((page, IRI(SKOS + "prefLabel"), lit(v[0], lang=lang)))
                seen.add(label_key(v[0]))
        alts = [(norm_label(v), lang, ds) for v, lang, ds, t, _s in merged_facts.get("alt", [])
                if t == "literal" and ds not in AUTHORITY_ONLY]
        for v, lang, ds in sorted(alts + [x[:3] for x in labels], key=lambda x: (src_rank(x[2]), lang_rank(x[1]), x[0])):
            k = label_key(v)
            if k and k not in seen:
                seen.add(k)
                out.add((page, IRI(SKOS + "altLabel"), lit(v, lang=lang or None)))

        # life dates and places: of the record with the highest precedence; derived values follow their record
        order = lambda v: (rank_of(v), lang_rank(v[1]), v[0])
        for kind in ("birth", "death"):
            raws = sorted([v for v in merged_facts.get(kind, []) if v[3] == "literal" and v[0].strip()], key=order)
            norms = sorted([v for v in merged_facts.get(kind + "N", []) if v[3] == "literal"], key=order)
            if raws:
                out.add((page, IRI(JLO + f"{kind}Date"), lit(raws[0][0].strip())))
            norm = next((n for n in norms if raws and n[4] == raws[0][4]), norms[0] if norms else None)
            if norm:
                dt = {4: "gYear", 7: "gYearMonth", 10: "date"}.get(len(norm[0]), "gYear")
                out.add((page, IRI(JLO + f"{kind}DateNormalized"), lit(norm[0], XSD + dt)))
            places = sorted([v for v in merged_facts.get(kind + "Place", []) if v[3] == "literal" and v[0].strip()], key=order)
            uris = sorted([v for v in merged_facts.get(kind + "PlaceURI", []) if v[3] == "uri"], key=order)
            if places:
                out.add((page, IRI(JLO + f"{kind}Location"), lit(places[0][0].strip())))
            uri = next((u for u in uris if places and u[4] == places[0][4]), uris[0] if uris else None)
            if uri:
                out.add((page, IRI(JLO + f"{kind}LocationURI"), iri(uri[0])))
        places = sorted([v for v in merged_facts.get("burialPlace", []) if v[3] == "literal" and v[0].strip()], key=order)
        uris = sorted([v for v in merged_facts.get("burialPlaceURI", []) if v[3] == "uri"], key=order)
        if places:
            out.add((page, IRI(JLO + "burialLocation"), lit(places[0][0].strip())))
        uri = next((u for u in uris if places and u[4] == places[0][4]), uris[0] if uris else None)
        if uri:
            out.add((page, IRI(JLO + "burialLocationURI"), iri(uri[0])))

        # occupations: text, and IRIs as jl:occupationURI
        occ_seen = set()
        for v, _l, ds, t, _s in sorted(merged_facts.get("occupation", []), key=lambda x: (src_rank(x[2]), x[0])):
            if t == "uri":
                out.add((page, IRI(JLO + "occupationURI"), iri(v)))
            elif v.strip() and v.strip().lower() not in occ_seen:
                occ_seen.add(v.strip().lower())
                out.add((page, IRI(JLO + "occupation"), lit(v.strip())))
        for v, _l, _ds, t, _s in merged_facts.get("occupationURI", []):
            if t == "uri":
                out.add((page, IRI(JLO + "occupationURI"), iri(v)))

        # descriptions: the best per preferred language, and the best in another language (40 characters or more)
        abstracts = [v for v in merged_facts.get("abstract", []) if v[3] == "literal" and len(v[0].strip()) >= 40]
        for lang in LANGUAGES:
            a = min((v for v in abstracts if v[1] == lang), key=order, default=None)
            if a:
                out.add((page, IRI(JLO + "hasAbstract"), lit(a[0].strip(), lang=lang)))
        other = min((v for v in abstracts if v[1] not in LANGUAGES), key=order, default=None)
        if other:
            out.add((page, IRI(JLO + "hasAbstract"), lit(other[0].strip(), lang=other[1] or None)))

        if c == "Place":
            w = wkt_of(merged_facts, rank_of)
            if w:
                out.add((page, IRI(GEO + "asWKT"), lit(canonical_wkt(w), GEO + "wktLiteral")))

        # records, external identifiers, web pages
        for m in members:
            out.add((page, IRI(JLSAME), iri(m)))   # replaces jl:represents (decision 0029)
        for v, _l, _ds, t, _s in merged_facts.get("sameAs", []):   # every identifier; a replaced one as its successor
            if t == "uri" and not v.startswith(JL) and not v.startswith("https://data.judaicalink.org/"):
                out.add((page, IRI(SAME), current_iri(v)))
        for v, _l, _ds, t, _s in merged_facts.get("gndId", []):
            if t == "literal" and re.fullmatch(r"[0-9]+[0-9X-]*", v.strip()):
                out.add((page, IRI(SAME), current_iri("https://d-nb.info/gnd/" + v.strip().upper())))
        for v, _l, _ds, t, _s in merged_facts.get("describedAt", []):
            if v.startswith("http"):
                out.add((page, IRI(RDFS + "seeAlso"), iri(v)))

    # 6. report: conflicts that point to mistakes in the data (0022)
    conflicts = Counter()
    keys_of = defaultdict(set)
    for s, k, *_ in links:
        keys_of[cl.find(s)].add(k)
    def closely_linked(keys):
        """Several GeoNames features of one place (a city, its municipality and district, 0032): connected through
        pairs that share a name and lie within 25 km."""
        feats = []
        for k in keys:
            f = facts.get(JL + "geonames/" + k.split(":", 1)[1], {})
            names = {label_key(v[0]) for field in ("label", "alt") for v in f.get(field, []) if v[3] == "literal"}
            m = re.match(r"\s*POINT\s*\(\s*(-?[0-9.]+)\s+(-?[0-9.]+)\s*\)", f["wkt"][0][0]) if f.get("wkt") else None
            if not names or not m:
                return False
            feats.append((names, float(m.group(2)), float(m.group(1))))
        reached, todo = {0}, [0]
        while todo:
            na, la, lo = feats[todo.pop()]
            for j, (nb, lb, mb) in enumerate(feats):
                if j in reached or not (na & nb):
                    continue
                d = 6371 * 2 * math.asin(math.sqrt(math.sin(math.radians(lb - la) / 2) ** 2 + math.cos(math.radians(la))
                                                   * math.cos(math.radians(lb)) * math.sin(math.radians(mb - lo) / 2) ** 2))
                if d <= 25:
                    reached.add(j)
                    todo.append(j)
        return len(reached) == len(feats)

    for root, members in sorted(groups.items()):
        sets = [set().union(*classes[m].values()) & {"Person", "Place", "Organization", "Work"} for m in members]
        sets = [x for x in sets if x]
        if any(contradict(a, b) for i, a in enumerate(sets) for b in sets[i + 1:]):
            conflicts["incompatible classes"] += 1
            run.log(f"conflict {iri_of[root]}: incompatible classes {sorted(members)[:8]}")
        # several identifiers of one authority: all are linked, the first record by record_order gives the facts;
        # replaced identifiers are written as their successors (decision 0029)
        for prefix, name in AUTHORITY_KEYS.items():
            ks = sorted(k for k in keys_of[root] if k.startswith(prefix + ":"))
            if not ks:
                continue
            cur = sorted({current_key(k) for k in ks})
            old = [k for k in ks if current_key(k) != k]
            if len(cur) > 1 and prefix == "geonames" and closely_linked(cur):
                conflicts["several GeoNames identifiers, closely linked (same name, near)"] += 1
            elif len(cur) > 1:
                conflicts[f"several {name} identifiers"] += 1
                run.log(f"conflict {iri_of[root]}: several {name} identifiers {', '.join(cur)} {sorted(members)[:8]}")
            if old:
                conflicts[f"replaced {name} identifiers"] += 1
                run.log(f"conflict {iri_of[root]}: replaced {name} identifiers "
                        + ", ".join(f"{k} -> {current_key(k)}" for k in old))
    shared = Counter((k, ds) for s, k, ds, *_ in set(links) if not k.startswith(JL))
    for (k, ds), n in sorted(shared.items()):
        if n >= 20 and not k.startswith(("gnd:", "viaf:", "wd:")):
            run.log(f"key shared by {n} records of {ds}: {k}")
    for e, parts in split_report:
        run.log(f"split {e}: {parts} (records before: {sorted(prev_pages[e])[:6]})")
    for e, target in sorted(merged.items()):
        run.log(f"merged {e} into {target}")

    run.note(f"{dict(stats)}; classes {dict(by_class)}; conflicts {dict(conflicts)}.")
    run.write_turtle("ep.ttl.gz", set(canonical_triples(out)))
    run.write_turtle("ep-history.ttl.gz", history)
