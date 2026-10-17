"""nrwbibdjg: the Bibliografie deutsch-jüdische Geschichte Nordrhein-Westfalen (Steinheim-Institut), made from the
answers of its OPAC to a search by GND number, true to the source (decision 0026, as bhr and hhkeydocs).

Input inputs:nrwbibdjg/opac-2026-10-17 (harvest.py): the BEACON of the bibliography (GND numbers of persons, places
and organisations) and, for each number, the OPAC's list of its titles (gnd/<number>.html). Each title is an item with
the bibliography's id (a UUID), a COinS (title, first author, year), the authors or editors ("(Hg.)"), the title, the
rest of the citation (place and year, or "In: ..." with the journal or volume and its id), a link to an online
resource, and the GND entries involved (authors, editors, subjects) with their names. The COinS breaks at an "&" in
the title and names only the first author, so the list's own text is taken.

Records:
- one per GND number of the BEACON, data/nrwbibdjg/<GND number> (the IRIs of 2024-05-24): the class of the GND entry
  (foaf:Person, foaf:Organization, schema:Place) from gnd/2026-10-16, as the source does not say; foaf:Person for a
  number the GND has deleted (undifferentiated names); skos:prefLabel and foaf:name the name the bibliography gives;
  owl:sameAs the GND; jl:describedAt the OPAC's list of its titles.
- one per title, data/nrwbibdjg/work/<UUID>, schema:CreativeWork: dc:title ("[Online-Ressource]" taken off),
  dcterms:issued the year of the COinS, dc:creator / dc:contributor the names of the authors / editors, gndo:author /
  gndo:editor the record of a GND entry of the item with that name, dcterms:subject the records of the other GND
  entries, dcterms:bibliographicCitation the rest of the citation, dcterms:isPartOf the journal or volume,
  rdfs:seeAlso the online resource, jl:describedAt the bibliography's page of the title.
- one per journal or volume, data/nrwbibdjg/work/<id> (the bibliography's id, z… journals, _b… volumes),
  schema:CreativeWork: dc:title; jl:describedAt the OPAC's list of its contents.
- Replacements: a work of 2024-05-24 (its IRI made from the title) is dcterms:isReplacedBy the works with that title
  in the lists of its GND numbers; failing that, by the only work with that title. Records of 2024-05-24 without a
  successor are owl:deprecated true.
"""

import gzip
import html
import re
import tarfile
import unicodedata
import urllib.parse
from collections import Counter, defaultdict

from jl import classes
from jl.generator import GeneratorError
from jl.iris import canonical_triples
from jl.rdf import IRI, RDF_TYPE, XSD, Literal
from jl.turtle import PREFIXES

INPUTS = {"pages": "inputs:nrwbibdjg/opac-2026-10-17/nrwbibdjg-pages-2026-10-17.tar.gz",
          "beacon": "inputs:nrwbibdjg/opac-2026-10-17/beacon.txt",
          "gnd": "gnd/2026-10-16/gnd.ttl.gz",
          "gnd-selection": "gnd/2026-10-16/gnd-selection.tsv.gz",
          "previous": "nrwbibdjg/2024-05-24"}
PARAMS = {}

NS = "http://data.judaicalink.org/data/nrwbibdjg/"
OPAC = "https://www.steinheim-institut.de/ebib-djg-nrw/"
LIST = OPAC + "query.html?database=NRW-Bibliografie&text1={}&kategorie1=gnd"
GND = "https://d-nb.info/gnd/"
GNDO = "https://d-nb.info/standards/elementset/gnd#"
JLO, SKOS, RDFS, FOAF, DC, DCT, OWL = (PREFIXES[p] for p in ("jl", "skos", "rdfs", "foaf", "dc", "dcterms", "owl"))
XSD_BOOLEAN = XSD + "boolean"
# numbers of the BEACON that gnd/2026-10-16 does not have (linked by no stable version), classed by their name
NOT_IN_GND = {"7777102-3": classes.ORGANISATION}   # Jüdische Gemeinde Reken
GND_RECORD = re.compile(r"^https?://data\.judaicalink\.org/data/gnd/(.+)$")

ITEM = re.compile(r'<li id="([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})">(.*?)<hr>\s*</div></span></li>',
                  re.S)
COINS = re.compile(r'<span class="cite Z3988" title="([^"]*)"')
AUTHOR = re.compile(r'<a class="autor"[^>]*>([^<]*)</a>')
CONTAINER = re.compile(r'<a class="zeitschrift" href="[^"]*text1=([^&"]+)&amp;kategorie1=(\w+)"[^>]*>([^<]*)</a>')
ENTRY = re.compile(r'text1=([0-9X-]+)&amp;kategorie1=gnd" title="[^"]*">([^<]*)</a>')
COINS_READ = {"ctx_ver", "rft_val_fmt", "rft.genre", "rft.atitle", "rft.au", "rft.date"}
COINS_EMPTY = {"rfr_id", "rft_id", "rft.jtitle", "rft.volume", "rft.issue", "rft.pages"}   # always empty
ONLINE = re.compile(r'<a target="_blank" href="([^"]+)"> → Ressource in externer Webseite betrachten')


def text(x):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x))).strip()


def old_iri(title):
    """The IRI of 2024-05-24 for a title (judaicalink-generators@68c9692: the title cleaned, then clean_url_string)."""
    t = title.replace("  ", "").replace("[Online-Ressource]", "").replace("\n", "").replace("\\", "")
    t = " ".join(t.strip().split())
    for a, b in (("'", ""), ('"', ""), (",", "_"), ("<<", ""), (">>", ""), ("|", "_"), (" ", ""), ("<", "_"),
                 (">", "_"), (".", ""), ("[", ""), ("]", ""), ("(", ""), (")", ""), ("{", ""), ("}", ""), ("#", ""),
                 ("-", ""), ("?", "")):
        t = t.replace(a, b)
    return NS + unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("utf-8")


def parse(page):
    """The items of a list page: {uuid, coins, persons (the authors or editors), role (author or editor), title,
    rest, container (id, kind, title), online, entries [(GND, name)]}."""
    items = []
    for uuid, body in ITEM.findall(page):
        m = COINS.search(body)
        coins = urllib.parse.parse_qs(html.unescape(m.group(1)), keep_blank_values=True) if m else {}
        content = body.partition('<p style="text-align:right">')[0]
        head, sep, tail = content.partition('<span class="lit_title">')
        if sep and '<div class="inbuch">' not in head:
            title, _, rest = tail.partition("</span>")
        else:   # no title: the authors, then the rest
            head, _, inbuch = content.partition('<div class="inbuch">')
            title, rest = "", re.sub(r'<span class="lit_person">.*?</span>\s*:?', "", head, flags=re.S) + " " + inbuch
        c = CONTAINER.search(rest)
        online = ONLINE.search(rest)
        rest = re.sub(r"<a [^>]*>[^<]*Ressource in externer Webseite betrachten[^<]*</a>", "", rest)
        items.append({"uuid": uuid, "coins": coins, "title": text(re.sub(r"<a [^>]*>\s*</a>", "", title)) or None,
                      "rest": re.sub(r"^[.:]\s*", "", text(rest)) or None,
                      "persons": [text(a) for a in AUTHOR.findall(head)],
                      "role": "editor" if re.search(r"</span>\s*\(Hg\.\)\s*:", head) else "author",
                      "container": (html.unescape(c.group(1)), c.group(2), text(c.group(3))) if c else None,
                      "online": html.unescape(online.group(1)) if online else None,
                      "entries": [(g, text(n)) for g, n in ENTRY.findall(body)]})
    if len(items) != page.count('<li id="'):
        raise GeneratorError(f"{page.count('<li id=')} items, {len(items)} read")
    return items


def coins_values(coins, key):
    return [v.strip() for v in coins.get(key, []) if v.strip()]


def generate(run):
    beacon = [line.strip() for line in run.input("beacon").read_text(encoding="utf-8").splitlines()
              if line.strip() and not line.startswith("#")]
    pages = {}
    with tarfile.open(run.input("pages"), "r:gz") as tar:
        for m in tar.getmembers():
            if mm := re.match(r"^gnd/([0-9X-]+)\.html$", m.name):
                pages[mm.group(1)] = tar.extractfile(m).read().decode("utf-8")
    missing = [n for n in beacon if n not in pages]
    if missing:
        raise GeneratorError(f"no list for {len(missing)} GND numbers of the BEACON, e.g. {missing[:5]}")

    stats = Counter()
    works = {}                       # uuid -> item
    lists = defaultdict(set)         # uuid -> GND numbers whose list has it
    names = defaultdict(Counter)     # GND number -> names given in the items
    for n in beacon:
        items = parse(pages[n])
        stats["lists without titles"] += not items
        for it in items:
            lists[it["uuid"]].add(n)
            for g, name in it["entries"]:
                names[g][name] += 1
            if it["uuid"] in works and works[it["uuid"]] != it:
                stats["items differing between lists"] += 1
                run.log("item differs between lists:", it["uuid"])
            works.setdefault(it["uuid"], it)
    stats["items in the lists"] = sum(len(v) for v in lists.values())

    # the class of each GND entry, from the gnd dataset (through the current number of a number the GND replaced)
    current = {}
    with gzip.open(run.input("gnd-selection"), "rt", encoding="utf-8") as f:
        for line in f:
            c = line.rstrip("\n").split("\t")
            if c[0] != "gnd":
                current[c[0]] = c[1]
    wanted = {current.get(n) or n for n in beacon}
    kinds = defaultdict(set)
    for s, p, o in run.triples("gnd"):
        if p == RDF_TYPE and (m := GND_RECORD.match(s)) and m.group(1) in wanted:
            k = classes.current(str(o))
            if classes.kind(k):
                kinds[m.group(1)].add(k)

    t = set()
    add = lambda s, p, o: o is not None and t.add((s, IRI(p), o))
    records = set()
    for n in beacon:
        s = IRI(NS + n)
        records.add(str(s))
        k = kinds.get(current.get(n) or n, set())
        if not k and n in NOT_IN_GND:
            k = {NOT_IN_GND[n]}
        if not k and n in current and not current[n] and "-" not in n:
            k = {classes.PERSON}   # not in the GND any more: an undifferentiated name (Tn), a person
            stats["records: Person (GND number deleted)"] += 1
        if len(k) == 1:
            t.add((s, IRI(RDF_TYPE), IRI(next(iter(k)))))
            stats["records: " + classes.kind(next(iter(k)))] += 1
        else:
            stats["records without class (not in gnd)" if not k else "records with several classes"] += 1
            run.log("record without one class:", n, sorted(k))
        if names[n]:
            name, _ = names[n].most_common(1)[0]
            add(s, SKOS + "prefLabel", Literal(name))
            add(s, FOAF + "name", Literal(name))
            if len(names[n]) > 1:
                run.log("several names for", n, dict(names[n]))
        else:
            stats["records without a name (no titles)"] += 1
        add(s, OWL + "sameAs", IRI(GND + n))
        add(s, JLO + "describedAt", IRI(LIST.format(n)))

    outside = Counter()
    containers = defaultdict(set)    # id -> {(kind, title)}
    for uuid, it in sorted(works.items()):
        w = IRI(NS + "work/" + uuid)
        t.add((w, IRI(RDF_TYPE), IRI(classes.WORK)))
        c = it["coins"]
        title = it["title"]   # the COinS has the same title, but breaks at an "&" in it
        if title and title.endswith(" [Online-Ressource]"):
            title = title[:-len(" [Online-Ressource]")]
            stats["works: [Online-Ressource] taken off the title"] += 1
        if [title] != coins_values(c, "rft.atitle") and title and "&" not in title:
            stats["works: title of the COinS differs from the list's"] += 1
            run.log("title differs:", uuid, repr(title), coins_values(c, "rft.atitle"))
        add(w, DC + "title", Literal(title) if title else None)
        stats["works without a title"] += not title
        for d in coins_values(c, "rft.date"):
            add(w, DCT + "issued", Literal(d))
        au = coins_values(c, "rft.au")
        if au and au != it["persons"][:1]:
            stats["works: author of the COinS not the list's first"] += 1
            run.log("COinS author differs:", uuid, au, it["persons"])
        for a in it["persons"]:
            add(w, DC + ("creator" if it["role"] == "author" else "contributor"), Literal(a))
        stats[f"works: {it['role']}s named"] += len(it["persons"])
        for g, name in it["entries"]:
            if NS + g not in records:
                outside[g] += 1
            elif name in it["persons"]:
                add(w, GNDO + it["role"], IRI(NS + g))
                stats[f"works: {it['role']} links"] += 1
            else:
                add(w, DCT + "subject", IRI(NS + g))
                stats["works: subject links"] += 1
        add(w, DCT + "bibliographicCitation", Literal(it["rest"]) if it["rest"] else None)
        if it["container"]:
            cid, kind, ctitle = it["container"]
            containers[cid].add((kind, ctitle))
            add(w, DCT + "isPartOf", IRI(NS + "work/" + urllib.parse.quote(cid)))
        if it["online"] and re.match(r"^https?://\S+$", it["online"]):
            add(w, RDFS + "seeAlso", IRI(it["online"]))
        add(w, JLO + "describedAt", IRI(OPAC + uuid + ".html"))
        for k in c:   # (an "&" in the title gives keys made of its rest)
            if k.startswith(("rft", "rfr", "ctx")) and k not in COINS_READ | COINS_EMPTY or (
                    k in COINS_EMPTY and coins_values(c, k)):
                stats[f"COinS field not taken over: {k}"] += 1
    stats["works"] = len(works)
    for cid, v in sorted(containers.items()):
        w = IRI(NS + "work/" + urllib.parse.quote(cid))
        kind, ctitle = sorted(v)[0]
        if len(v) > 1:
            run.log("container with several titles:", cid, sorted(v))
        t.add((w, IRI(RDF_TYPE), IRI(classes.WORK)))
        add(w, DC + "title", Literal(ctitle) if ctitle else None)
        add(w, JLO + "describedAt", IRI(OPAC + "query.html?database=NRW-Bibliografie&text1="
                                        + urllib.parse.quote(cid) + "&kategorie1=" + kind))
        stats[f"containers: {kind}"] += 1
    if outside:
        stats["GND entries in the items that are not in the BEACON"] = len(outside)
        run.log("GND entries not in the BEACON:", dict(outside.most_common(20)))

    # replacements of the records of 2024-05-24
    # (2024-05-24 also took the titles of the journals and volumes as works)
    by_title = defaultdict(set)
    for uuid, it in works.items():
        if it["title"]:
            by_title[old_iri(it["title"])].add(uuid)
        if it["container"]:
            cid = urllib.parse.quote(it["container"][0])
            lists[cid] |= lists[uuid]
            if it["container"][2]:
                by_title[old_iri(it["container"][2])].add(cid)
    old_types, old_lists = {}, defaultdict(set)
    for s, p, o in run.triples("previous"):
        if p == RDF_TYPE:
            old_types[str(s)] = str(o)
        elif p == JLO + "describedAt":
            if m := re.search(r"text1=([^&]+)&", o.value if isinstance(o, Literal) else str(o)):
                old_lists[str(s)].add(m.group(1))
    rep = Counter()
    for s, cls in sorted(old_types.items()):
        if s in records:
            rep["records: same IRI"] += 1
            continue
        if not cls.endswith("Work"):
            t.add((IRI(s), IRI(OWL + "deprecated"), Literal("true", XSD_BOOLEAN)))
            rep["records: deprecated"] += 1
            run.log("previous record deprecated:", s)
            continue
        cand = by_title.get(s, set())
        new = {u for u in cand if lists[u] & old_lists[s]}
        how = "by title and GND number"
        if not new and len(cand) == 1:
            new, how = cand, "by title alone"
        for u in sorted(new):
            t.add((IRI(s), IRI(DCT + "isReplacedBy"), IRI(NS + "work/" + u)))
        if new:
            rep[f"works: replaced {how}" + (" (several)" if len(new) > 1 else "")] += 1
        else:
            t.add((IRI(s), IRI(OWL + "deprecated"), Literal("true", XSD_BOOLEAN)))
            rep["works: deprecated" + (" (several candidates)" if cand else "")] += 1
            run.log("previous work deprecated:", s, "candidates:", len(cand))

    run.note(f"{dict(sorted(stats.items()))}; previous records: {dict(sorted(rep.items()))}.")
    run.write_turtle("nrwbibdjg.ttl.gz", set(canonical_triples(t)))   # docs/iri-forms.md
