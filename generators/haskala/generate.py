"""haskala: the Library of Haskala, made from the Drupal 7 database of haskala-library.net (decision 0024: made again
from the source).

Source: inputs:haskala/drupal-2015-04-20, the content tables of the database dump of 2015-04-20 (make_input.py). The
database holds the research data of a German-Israeli project (2004-2010), migrated into Drupal in April 2015 and not
changed after; it was hosted by the Judaica Division of the Frankfurt University Library.

Everything of the database is stated, so that it can be rebuilt from the data without the portal (decided
2026-10-13): every node of the seven content types (person, book, edition, mention, production, preface,
translation; not the one page of site text), every field value and every taxonomy term. The schema is stated as well
(haskala-vocabulary.ttl.gz): a class per content type, a property per field (the Drupal machine name without
"field_"), with type, cardinality, target vocabulary or content type and allowed values, and per content type and
field an instance with the Drupal label, help text, order and whether it is shown. The sections of the book
pages, which the database does not store, are read from the archived pages (inputs:haskala/wayback-books-2026-10-13):
every section and heading (vocab:Section, in the order of the pages), the section of each book field (vocab:section)
and the sections in which editions, mentions, productions, prefaces and translations were shown
(vocab:shownInSection). Terms are coined in the dataset
namespace, data/haskala/vocab/. Field values: text in Drupal's HTML formats as rdf:HTML (the notes mark chronograms
with <strong> and <ins>), other text as given, yes/no fields as xsd:boolean, numbers as xsd:integer, taxonomy and
content references as IRIs, links as IRIs, coordinates as geosparql:asWKT in the form of geo-coordinates.

IRIs: data/haskala/<content type>/<node id>, data/haskala/<vocabulary>/<term id> (the term), data/haskala/<vocabulary>
(the scheme). Every node and term: rdfs:label (the title or name), jl:describedAt (its page on haskala-library.net),
dcterms:identifier (the record id of the research database, from the migration maps, where there is one). Mapped to
JudaicaLink terms in addition: persons foaf:Person, skos:prefLabel (the German name, else the title), skos:altLabel
(the Hebrew name, the pseudonym), owl:sameAs VIAF, jl:birthDate/jl:deathDate and the places as given; books schema:CreativeWork
with skos:prefLabel; terms skos:Concept with skos:prefLabel, skos:inScheme, skos:broader; cities also schema:Place.

From 2019-07-01: its 194 persons of the library are dcterms:isReplacedBy the person node of their page (matched by
the page address, which Drupal treats without case); their GND links, from the 2019 working list and not in the
database, go to the new IRIs (haskala-gnd-2019.ttl.gz). The 32 persons of haskala.net (biographies of the University
of Potsdam, not in the database) keep their IRIs and their 2019 triples, with their occupations from Haskala_net.ttl
of 2025-03-24 (one value per occupation) and without empty values (haskala-net.ttl.gz).
"""

import html
import re
import unicodedata
from collections import Counter, defaultdict
from urllib.parse import unquote

from jl import classes
from jl.generator import GeneratorError, load_shared
from jl.rdf import IRI, RDF_TYPE, XSD, Literal
from jl.turtle import PREFIXES

drupal = load_shared("haskala", "drupal_sql")

INPUTS = {
    "drupal": "inputs:haskala/drupal-2015-04-20/haskala-drupal-2015-04-20.sql.gz",
    "previous": "haskala/2019-07-01",
    "net": "haskala/2025-03-24/Haskala_net.ttl.gz",
    "pages": "inputs:haskala/wayback-books-2026-10-13",   # fetched by fetch_wayback.py
}
PARAMS = {}

NS = "http://data.judaicalink.org/data/haskala/"
V = NS + "vocab/"
SITE = "https://www.haskala-library.net/"
JLO, SKOS, RDFS, FOAF, OWL, DCT = (PREFIXES[p] for p in ("jl", "skos", "rdfs", "foaf", "owl", "dcterms"))
RDF = PREFIXES["rdf"]
WKT = "http://www.opengis.net/ont/geosparql#asWKT"
HTML = RDF + "HTML"
BUNDLES = ("person", "book", "edition", "mention", "production", "preface", "translation")
HTML_FORMATS = {"filtered_html", "full_html"}
TITLE = re.compile(r"(.*[^\s]) - ([\u0590-\u05FF].*)")

# The schema terms: (local name, kind, label, comment)
META = [
    ("FieldInstance", "class", "Field of a content type",
     "A field as used by one content type: its label, help text and order there."),
    ("drupalBundle", "property", "Drupal content type", "The machine name of the Drupal content type of a class."),
    ("titleLabel", "property", "Label of the title", "The label of the node title (rdfs:label) of a content type."),
    ("drupalField", "property", "Drupal field", "The machine name of the Drupal field a property states."),
    ("drupalFieldType", "property", "Drupal field type", "The Drupal type of the field (text, list_boolean, ...)."),
    ("cardinality", "property", "Cardinality", "How many values the field takes; -1 for any number."),
    ("targetScheme", "property", "Target vocabulary", "The taxonomy whose terms the field takes."),
    ("targetClass", "property", "Target content type", "The content type whose nodes the field takes."),
    ("allowedValue", "property", "Allowed value", "A value of a list field, as 'key = label'."),
    ("contentType", "property", "Content type", "The class (content type) of a field instance."),
    ("field", "property", "Field", "The property (field) of a field instance."),
    ("required", "property", "Required", "Whether the field must have a value."),
    ("weight", "property", "Weight", "The order of a field on the page, or of a term in its vocabulary (lower first)."),
    ("hidden", "property", "Hidden", "Whether the field is not shown on the page of the node."),
    ("drupalVocabulary", "property", "Drupal vocabulary", "The machine name of the Drupal taxonomy of a scheme."),
    ("Section", "class", "Section of the book page",
     "A section of the page of a book on haskala-library.net, or a part of a section under its own heading; read "
     "from the archived pages."),
    ("section", "property", "Section", "The section of the book page in which a field is shown."),
    ("shownInSection", "property", "Shown in section",
     "A section of the book page in which the nodes of a content type linked to the book are shown."),
]


def table(t, name):
    cols = t[name]["columns"]
    return [dict(zip(cols, r)) for r in t[name]["rows"]]


def lit(v, dt=None):
    return Literal(str(v), dt)


def boolean(v):
    return Literal("true" if v else "false", XSD + "boolean")


def number(v):
    return Literal(str(int(v)), XSD + "integer")


def wkt(lat, lng):
    def f(x):
        s = repr(float(x))
        return s if s.startswith("-") else "+" + s
    return f"Point ( {f(lng)} {f(lat)} )"


TOKEN = re.compile(r'<section id="(top-details|bottom-details)"|class="tab-sub-title[^"]*">\s*([^<]*?)\s*</div>'
                   r'|class="fields-group-name">\s*([^<]*?)\s*</div>|class="field field-name-(field-[a-z0-9-]+)')
MAIN = "Main part"


def slug(label):
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def sections(run, inst_iri, filled, cls, schema, add, n):
    """The section (and the heading within it) of every field shown on the archived book pages. The page has a main
    part under the title and tabs ("fields groups"); both can have headings ("tab sub titles"). Fields of other
    content types shown on the book page (editions, mentions, productions, prefaces, ...) give the sections in
    which these content types are shown."""
    seen = defaultdict(Counter)
    pages = [p for p in run.inputs("pages") if p.name.startswith("book-")]
    position = defaultdict(list)   # (group, sub) -> its relative position on each page where it appears
    ahead = Counter()              # (tab a, tab b) -> on how many pages a comes before b in the navigation
    for path in pages:
        group, sub = None, None
        order = []
        text = path.read_text(encoding="utf-8", errors="replace")
        nav = text[text.find('id="details-navigation"'):text.find("</nav>", text.find('id="details-navigation"'))]
        tabs = [html.unescape(x).strip() for x in re.findall(r'<li><a href="#[^"]*">([^<]*)</a></li>', nav)]
        for i, a in enumerate(tabs):
            for b in tabs[i + 1:]:
                ahead[(a, b)] += 1
        for m in TOKEN.finditer(text):
            if m.group(1):
                group, sub = (MAIN if m.group(1) == "top-details" else None), None
            elif m.group(2) is not None:
                sub = html.unescape(m.group(2)).strip() or None
            elif m.group(3) is not None:
                group, sub = html.unescape(m.group(3)).strip(), None
            elif m.group(4) and group:
                seen[m.group(4).replace("-", "_")][(group, sub)] += 1
                for w in ((group, None), (group, sub)):
                    if w not in order:
                        order.append(w)
        for i, w in enumerate(order):
            position[w].append(i / len(order))
    owners = defaultdict(set)   # the content types that have values in a field (book has field_role, never filled)
    for (bundle, fname) in inst_iri:
        if (bundle, fname) in filled:
            owners[fname].add(bundle)
    placed, shown = {}, defaultdict(set)
    for fname, c in sorted(seen.items()):
        (where, k), = c.most_common(1)
        if len(c) > 1 and "book" in owners[fname]:
            run.log(f"{fname}: in several sections {dict(c)}; {where} taken")
        if "book" in owners[fname]:   # a field of the book (field_language is also on translations, shown in Editions)
            placed[fname] = where
        elif len(owners[fname]) == 1:   # a field of one other content type: where its nodes are shown
            for (group, _sub) in c:
                shown[next(iter(owners[fname]))].add(group)
    # the order: the main part, then the tabs in the order of the navigation of the pages (a tab comes before the
    # tabs it precedes on most pages; the order changed slightly over the years of the captures), each followed by
    # its headings in the order of the pages (mean relative position)
    mean = {w: sum(ps) / len(ps) for w, ps in position.items()}
    groups = {g for g, _s in position} - {MAIN}
    wins = {g: sum(1 for h in groups if ahead[(g, h)] > ahead[(h, g)]) for g in groups}
    tabs = sorted(groups, key=lambda g: (-wins[g], mean[(g, None)]))
    ranked = []
    for g in [MAIN] + tabs:
        ranked.append((g, None))
        ranked += sorted((w for w in position if w[0] == g and w[1]), key=lambda w: mean[w])
    iri = {}
    for rank, where in enumerate(ranked):
        group, sub = where
        s = f"{V}Book/section/{slug(group)}" + (f"/{slug(sub)}" if sub else "")
        iri[where] = s
        add(s, RDF_TYPE, V + "Section", schema)
        add(s, RDFS + "label", lit(sub or group), schema)
        add(s, V + "weight", number(rank), schema)
    for (group, sub), s in iri.items():
        if sub:
            add(s, PREFIXES["dcterms"] + "isPartOf", iri[(group, None)], schema)
    for fname, where in placed.items():
        add(inst_iri[("book", fname)][0], V + "section", iri[where], schema)
    for b, groups in shown.items():
        for g in groups:
            if (g, None) in iri:
                add(cls[b], V + "shownInSection", iri[(g, None)], schema)
    n["archived book pages"] = len(pages)
    n["book fields with their section"] = len(placed)
    n["book fields not on the archived pages"] = sum(1 for (b, f) in inst_iri if b == "book" and f not in placed)


def generate(run):
    t = drupal.tables(run.input("drupal"))
    n = Counter()
    data, schema = set(), set()

    def add(s, p, o, out=data):
        out.add((IRI(s), IRI(p), o if isinstance(o, Literal) else IRI(o)))

    # --- the schema -------------------------------------------------------------------------------
    vocabs = {r["vid"]: r for r in table(t, "taxonomy_vocabulary")}
    scheme = {r["machine_name"]: NS + r["machine_name"] for r in vocabs.values()}
    term_vocab = {r["tid"]: vocabs[r["vid"]]["machine_name"] for r in table(t, "taxonomy_term_data")}
    node_type = {r["nid"]: r["type"] for r in table(t, "node")}
    cls = {b: V + b.capitalize() for b in BUNDLES}
    if any(b in scheme for b in BUNDLES) or "vocab" in scheme:
        raise GeneratorError("a vocabulary has the name of a content type")

    def node_iri(nid):
        b = node_type[nid]
        if b not in BUNDLES:
            raise GeneratorError(f"reference to node {nid} of type {b}")
        return f"{NS}{b}/{nid}"

    def term_iri(tid):
        return f"{NS}{term_vocab[tid]}/{tid}"

    for name, kind, label, comment in META:
        add(V + name, RDF_TYPE, RDFS + "Class" if kind == "class" else RDF + "Property", schema)
        add(V + name, RDFS + "label", lit(label), schema)
        add(V + name, RDFS + "comment", lit(comment), schema)
    for r in table(t, "node_type"):
        if r["type"] not in BUNDLES:
            continue
        c = cls[r["type"]]
        add(c, RDF_TYPE, RDFS + "Class", schema)
        add(c, RDFS + "label", lit(r["name"]), schema)
        add(c, V + "drupalBundle", lit(r["type"]), schema)
        add(c, V + "titleLabel", lit(r["title_label"]), schema)
        if r["description"]:
            add(c, RDFS + "comment", lit(r["description"]), schema)
    for r in vocabs.values():
        s = scheme[r["machine_name"]]
        add(s, RDF_TYPE, SKOS + "ConceptScheme", schema)
        add(s, RDFS + "label", lit(r["name"]), schema)
        add(s, V + "drupalVocabulary", lit(r["machine_name"]), schema)
        if r["description"]:
            add(s, RDFS + "comment", lit(r["description"]), schema)

    fields = {r["field_name"]: (r, drupal.php_unserialize(r["data"])) for r in table(t, "field_config")
              if not r["deleted"]}
    instances = [(r, drupal.php_unserialize(r["data"])) for r in table(t, "field_config_instance")
                 if not r["deleted"] and (r["bundle"] in BUNDLES or r["entity_type"] == "taxonomy_term")]
    prop = {}
    for fname in fields:
        prop[fname] = WKT if fields[fname][0]["type"] == "geolocation_latlng" else V + re.sub(r"^field_", "", fname)
    labels = defaultdict(set)
    per_bundle = Counter((r["bundle"], d.get("label")) for r, d in instances)
    for r, d in instances:
        unique = per_bundle[(r["bundle"], d.get("label"))] == 1
        labels[r["field_name"]].add(d.get("label") if unique else None)
    for fname, (r, d) in sorted(fields.items()):
        if not any(i["field_name"] == fname for i, _d in instances):
            continue
        p = prop[fname]
        if p == WKT:
            continue
        st = d.get("settings", {}) or {}
        add(p, RDF_TYPE, RDF + "Property", schema)
        ls = labels[fname]
        label = next(iter(ls)) if len(ls) == 1 and None not in ls else fname[len("field_"):].replace("_", " ").capitalize() \
            if fname.startswith("field_") else fname.capitalize()
        add(p, RDFS + "label", lit(label), schema)
        add(p, V + "drupalField", lit(fname), schema)
        add(p, V + "drupalFieldType", lit(r["type"]), schema)
        add(p, V + "cardinality", number(r["cardinality"]), schema)
        if r["type"] == "taxonomy_term_reference":
            for a in (st.get("allowed_values") or {}).values():
                add(p, V + "targetScheme", scheme[a["vocabulary"]], schema)
        elif r["type"] == "entityreference":
            for b in ((st.get("handler_settings") or {}).get("target_bundles") or {}):
                add(p, V + "targetClass", cls[b], schema)
        elif r["type"].startswith("list_"):
            for k, v in (st.get("allowed_values") or {}).items():
                add(p, V + "allowedValue", lit(f"{k} = {v}"), schema)
    inst_iri = {}
    for r, d in instances:
        owner = cls.get(r["bundle"]) or scheme[r["bundle"]]
        local = r["field_name"][len("field_"):] if r["field_name"].startswith("field_") else r["field_name"]
        s = f"{V}{r['bundle'].capitalize() if r['bundle'] in BUNDLES else r['bundle']}/{local}"
        add(s, RDF_TYPE, V + "FieldInstance", schema)
        add(s, V + "contentType", owner, schema)
        add(s, V + "field", prop[r["field_name"]], schema)
        add(s, RDFS + "label", lit(d.get("label") or local), schema)
        if d.get("description"):
            add(s, RDFS + "comment", lit(d["description"]), schema)
        add(s, V + "required", boolean(d.get("required")), schema)
        display = (d.get("display") or {}).get("default") or {}
        if "weight" in display:
            add(s, V + "weight", number(display["weight"]), schema)
        add(s, V + "hidden", boolean(display.get("type") == "hidden"), schema)
        n["field instances"] += 1
        inst_iri[(r["bundle"], r["field_name"])] = (s, display.get("weight", 0))

    # --- the sections of the book pages, from the archived pages -------------------------------------
    filled = {(r["bundle"], name[len("field_data_"):]) for name in t if name.startswith("field_data_")
              for r in table(t, name)}
    sections(run, inst_iri, filled, cls, schema, add, n)

    # --- nodes and terms ----------------------------------------------------------------------------
    alias = {}
    for r in table(t, "url_alias"):
        m = re.fullmatch(r"(node|taxonomy/term)/([0-9]+)", r["source"])
        if m:
            alias[(m.group(1), int(m.group(2)))] = r["alias"]
    ident = {}
    for name in t:
        if not name.startswith("migrate_map_"):
            continue
        kind = "taxonomy/term" if name.endswith("termsmigrate") else "node"
        for r in table(t, name):
            ident[(kind, r["destid1"])] = r["sourceid1"]

    def common(s, kind, key, label):
        add(s, RDFS + "label", lit(label))
        if (kind, key) in alias:
            add(s, JLO + "describedAt", lit(SITE + alias[(kind, key)]))
        if (kind, key) in ident:
            add(s, DCT + "identifier", lit(ident[(kind, key)]))

    titles = {}
    for r in table(t, "node"):
        if r["type"] not in BUNDLES:
            n["nodes left out (" + r["type"] + ")"] += 1
            continue
        s = node_iri(r["nid"])
        titles[r["nid"]] = r["title"]
        add(s, RDF_TYPE, cls[r["type"]])
        common(s, "node", r["nid"], r["title"])
        if r["type"] == "book":
            add(s, RDF_TYPE, classes.WORK)
            add(s, SKOS + "prefLabel", lit(r["title"]))
        n["nodes " + r["type"]] += 1
    parents = defaultdict(list)
    for r in table(t, "taxonomy_term_hierarchy"):
        if r["parent"]:
            parents[r["tid"]].append(r["parent"])
    for r in table(t, "taxonomy_term_data"):
        v = term_vocab[r["tid"]]
        s = term_iri(r["tid"])
        add(s, RDF_TYPE, SKOS + "Concept")
        if v == "cities":
            add(s, RDF_TYPE, classes.PLACE)
        add(s, SKOS + "prefLabel", lit(r["name"]))
        add(s, SKOS + "inScheme", scheme[v])
        common(s, "taxonomy/term", r["tid"], r["name"])
        add(s, V + "weight", number(r["weight"]))
        if r["description"]:
            add(s, RDFS + "comment", lit(r["description"]))
        for p in parents[r["tid"]]:
            add(s, SKOS + "broader", term_iri(p))
        n["terms"] += 1

    # --- field values -------------------------------------------------------------------------------
    person = defaultdict(lambda: defaultdict(list))   # nid -> field -> values, for the JudaicaLink mapping
    for fname, (fc, _d) in fields.items():
        name = "field_data_" + fname
        if name not in t:
            continue
        ftype = fc["type"]
        for r in table(t, name):
            if r["deleted"]:
                continue
            if r["entity_type"] == "node":
                if node_type[r["entity_id"]] not in BUNDLES:
                    continue
                s = node_iri(r["entity_id"])
            else:
                s = term_iri(r["entity_id"])
            p = prop[fname]
            col = lambda c: r.get(f"{fname}_{c}")
            if ftype in ("text", "text_long", "text_with_summary"):
                v = col("value")
                if v is None or v == "":
                    continue
                o = lit(v, HTML if col("format") in HTML_FORMATS else None)
            elif ftype == "list_boolean":
                o = boolean(col("value"))
            elif ftype in ("number_integer", "list_integer"):
                o = number(col("value"))
            elif ftype == "list_text":
                o = lit(col("value"))
            elif ftype == "taxonomy_term_reference":
                o = IRI(term_iri(col("tid")))
            elif ftype == "entityreference":
                o = IRI(node_iri(col("target_id")))
            elif ftype == "link_field":
                o = IRI(col("url"))
            elif ftype == "geolocation_latlng":
                o = lit(wkt(col("lat"), col("lng")))
            else:
                raise GeneratorError(f"field type {ftype} ({fname}) not handled")
            add(s, p, o)
            n["field values"] += 1
            if r["entity_type"] == "node" and node_type[r["entity_id"]] == "person":
                person[r["entity_id"]][fname].append(o)

    # --- persons in JudaicaLink terms ---------------------------------------------------------------
    term_name = {r["tid"]: r["name"] for r in table(t, "taxonomy_term_data")}
    for nid, title in titles.items():
        if node_type[nid] != "person":
            continue
        s = node_iri(nid)
        f = person[nid]
        add(s, RDF_TYPE, FOAF + "Person")
        german = [o.value.strip() for o in f["field_german_name"] if o.value.strip()]
        alt = [o.value.strip() for k in ("field_hebrew_name", "field_pseudonym") for o in f[k] if o.value.strip()]
        m = TITLE.fullmatch(title)
        if not german and m:   # the title is "<name> - <Hebrew name>" where the German name field is empty
            german = [m.group(1).strip()]
            alt.append(m.group(2).strip())
            n["person labels from the title"] += 1
        add(s, SKOS + "prefLabel", lit(german[0] if german else title))
        for v in alt:
            if v != (german[0] if german else title):
                add(s, SKOS + "altLabel", lit(v))
        for o in f["field_viaf_id"]:
            if not re.fullmatch(r"[0-9]+", o.value.strip()):
                raise GeneratorError(f"person {nid}: VIAF id {o.value!r}")
            add(s, OWL + "sameAs", f"http://viaf.org/viaf/{o.value.strip()}")
            n["VIAF links"] += 1
        for k, p in (("field_date_of_birth", "birthDate"), ("field_date_of_death", "deathDate")):
            for o in f[k]:
                add(s, JLO + p, lit(o.value.strip()))
        for k, p in (("field_place_of_birth", "birthLocation"), ("field_place_of_death", "deathLocation")):
            for o in f[k]:
                add(s, JLO + p + "URI", o)
                add(s, JLO + p, lit(term_name[int(o.rsplit("/", 1)[1])]))

    # --- the IRIs of 2019 ------------------------------------------------------------------------------
    key = lambda a: unicodedata.normalize("NFC", a).lower()
    by_alias = {key(a): nid for (kind, nid), a in alias.items() if kind == "node" and node_type.get(nid) == "person"}
    old = defaultdict(list)
    for s, p, o in run.triples("previous", file="Haskala_enriched.ttl.gz"):
        old[str(s)].append((s, p, o))
    gnd, net = set(), set()
    for s, ts in sorted(old.items()):
        pages = [key(unquote(str(o).split("haskala-library.net/", 1)[1]).strip("/")) for _s, p, o in ts
                 if p == OWL + "sameAs" and "haskala-library.net/people/" in str(o)]
        if not pages:
            net.update(tr for tr in ts if not (isinstance(tr[2], Literal) and not tr[2].value.strip()))
            n["2019 persons of haskala.net"] += 1
            continue
        nids = sorted({by_alias[a] for a in pages if a in by_alias})
        if not nids:
            raise GeneratorError(f"{s}: page {pages} is no person of the database")
        for a in pages:
            if a not in by_alias:   # an address of the site in 2019 that the database of 2015 does not have
                run.log(f"{s}: page {a} not in the database, matched by its other page")
        if len(nids) > 1:   # 2019 joined persons that are two nodes of the database (its duplicates)
            run.log(f"{s}: replaced by {len(nids)} persons: " + ", ".join(titles[x] for x in nids))
            n["2019 persons replaced by several"] += 1
        n["2019 persons replaced"] += 1
        for nid in nids:
            new = node_iri(nid)
            add(s, DCT + "isReplacedBy", new)
            for _s, p, o in ts:
                m = re.fullmatch(r"https?://d-nb\.info/gnd/([0-9X-]+)", str(o)) if p == OWL + "sameAs" else None
                if m:
                    gnd.add((IRI(new), IRI(OWL + "sameAs"), IRI("http://d-nb.info/gnd/" + m.group(1))))
    net_persons = {s for s, _p, _o in net}
    for s, p, o in run.triples("net"):
        if p != JLO + "Occupation":
            continue
        if s not in net_persons:
            raise GeneratorError(f"{s}: a haskala.net person not among the 2019 persons of haskala.net")
        for v in o.value.split(","):
            if v.strip():
                net.add((s, IRI(JLO + "occupation"), Literal(v.strip())))
                n["haskala.net occupations"] += 1

    for k, c in sorted(n.items()):
        run.log(f"{k}: {c:,}")
    run.note(f"{sum(c for k, c in n.items() if k.startswith('nodes ') and 'left out' not in k):,} nodes, "
             f"{n['terms']} terms, {n['field values']:,} field values, {n['field instances']} field instances; "
             f"{n['VIAF links']} VIAF links. 2019: {n['2019 persons replaced']} persons replaced, "
             f"{len(gnd)} GND links carried over, {n['2019 persons of haskala.net']} haskala.net persons kept "
             f"({n['haskala.net occupations']} occupations).")
    run.write_turtle("haskala.ttl.gz", data)
    run.write_turtle("haskala-vocabulary.ttl.gz", schema)
    run.write_turtle("haskala-gnd-2019.ttl.gz", gnd)
    run.write_turtle("haskala-net.ttl.gz", net)
