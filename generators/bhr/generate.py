"""bhr: the Biographisches Handbuch der Rabbiner, made from the pages of the Biographisches Portal der Rabbiner
(Steinheim-Institut), true to the portal (decision 0026, as haskala and hhkeydocs).

Input inputs:bhr/portal-2026-10-16: the pages of all entries (harvest_portal.py) and the portal's BEACON. Each page:
the heading (the name with variants: "AACH, Löb (hebr. Juda-L.)", "EGER, Moses, bürgerlich Moses SCHLESINGER"), the
reference to the printed handbook ("BHR I.1, 121"), a list with birth ("Geb."), death ("Gest.") and the biography,
and sections (Dissertation, Dokumente, Manuskripte, Publikationen, Bildmaterialien, Epigraphik, Literatur), each a
list of texts. The box "Externe Quellen" shows the GND number of the entry and links that the portal looks up in DNB
EntityFacts; only the GND number is the portal's own statement, and the BEACON states it (all 805 agree).

Files:
- bhr.ttl.gz: one record per entry, data/bhr/<id> (the id without leading zeros, as the portal links and Wikidata
  P10405 write it), foaf:Person; rdfs:label the heading as given; skos:prefLabel the name (the heading up to its
  variants, the surname in capitals written as a name: "Aach, Löb"), skos:altLabel the variants introduced by
  auch, bürgerlich, gen., genannt, eigentlich, früher, vormals, verh.; jl:birthDate/jl:birthLocation and jl:deathDate/jl:deathLocation as the
  page gives them ("ca. 1750", "Trier"); jl:hasAbstract the biography (the other items of the list, one per line);
  dcterms:bibliographicCitation the reference to the printed handbook; jl:describedAt the page; jl:occupationURI
  data/occupation/Rabbi (parameter rabbi: the handbook is of rabbis; the 2018 version stated it for every person);
  the texts of the sections with the properties of the dataset's vocabulary (data/bhr/vocab/<section>), the
  publications and the dissertation also as jl:hasPublication.
- bhr-beacon.ttl.gz: the portal's BEACON, record owl:sameAs <https://d-nb.info/gnd/<n>> (the page of the GND number
  names the entry).
- bhr-vocabulary.ttl.gz: the properties of the sections.
- Replacements: every record of the version 2026-10-12 is dcterms:isReplacedBy the record(s) of its BHR id (the
  "id:<n>" of its jl:describedAt); a record without an id (the 2018 data has 368) by the record with the same name
  (skos:prefLabel, case and spaces ignored) if exactly one has it and no birth or death year contradicts. An old
  record with no such successor (other spellings, several candidates) is owl:deprecated true: the old IRIs made from
  names cannot always be matched; whoever has one on file looks up the entry in the portal and links its new IRI.
"""

import html
import io
import re
import tarfile
from collections import Counter, defaultdict

from jl.iris import canonical_triples
from jl.rdf import IRI, RDF_TYPE, XSD, Literal
from jl.turtle import PREFIXES

INPUTS = {"pages": "inputs:bhr/portal-2026-10-16/bhr-pages-2026-10-16.tar.gz",
          "beacon": "inputs:bhr/portal-2026-10-16/beacon.txt",
          "previous": "bhr/2026-10-12"}
PARAMS = {"rabbi": True}
XSD_BOOLEAN = XSD + "boolean"

JL = "http://data.judaicalink.org/data/"
BHR = JL + "bhr/"
VOCAB = BHR + "vocab/"
PAGE = "https://www.steinheim-institut.de/cgi-bin/bhr?id="
JLO, SKOS, RDFS, FOAF, DCT, OWL = (PREFIXES[p] for p in ("jl", "skos", "rdfs", "foaf", "dcterms", "owl"))
RABBI = JL + "occupation/Rabbi"
NO_ENTRY = "Eintrag nicht vorhanden"

# the sections of a page: (heading, property name, English label, German label)
SECTIONS = [("Dissertation", "dissertation", "dissertation", "Dissertation"),
            ("Dokumente", "document", "document", "Dokument"),
            ("Manuskripte", "manuscript", "manuscript", "Manuskript"),
            ("Publikationen", "publication", "publication", "Publikation"),
            ("Bildmaterialien", "image", "image", "Bildmaterial"),
            ("Epigraphik", "epigraphy", "epigraphy (gravestone)", "Epigraphik (Grabstein)"),
            ("Literatur", "literature", "literature", "Literatur")]
AS_PUBLICATION = {"Dissertation", "Publikationen"}
VARIANT = re.compile(r",\s*(?:auch|bürgerlich|gen\.|genannt|eigentlich|früher|vormals|verh\.)\s+([^,]+)")


def text(x):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x))).strip()


def as_name(s):
    """Surnames written in capitals as names: "AACH, Löb" -> "Aach, Löb"."""
    return re.sub(r"\b([A-ZÄÖÜ][A-ZÄÖÜß'-]+)\b", lambda m: m.group(1).capitalize()
                  if len(m.group(1)) > 1 else m.group(1), s)


def names(heading):
    """(preferred name, [variants]) from the heading "SURNAME, given names, further information": the name is the
    first two parts; variants are the names introduced by auch, bürgerlich, gen., genannt, eigentlich, früher,
    vormals, verh. Titles, abbreviated Hebrew forms and remarks stay only in the heading (rdfs:label)."""
    h = re.sub(r"\s*\(hebr\.[^)]*\)", "", heading).strip()
    parts = [x.strip() for x in h.split(",")]
    main = ", ".join(parts[:2]) if len(parts) > 1 else parts[0]
    variants = [v for v in (m.group(1).strip(" „“\"") for m in VARIANT.finditer(h)) if v]
    return as_name(main), [as_name(v) for v in variants]


def life(item, word):
    """(date, place) of an item "Geb. ca. 1750 in Trier,"."""
    rest = item[len(word):].strip().rstrip(",").strip()
    date, sep, place = rest.partition(" in ")
    if not sep and rest.startswith("in "):
        date, place = "", rest[3:]
    return date.strip(" ,"), place.strip(" ,")


def parse(page):
    art = page[page.find("<article>"):page.find("<aside>") if "<aside>" in page else len(page)]
    heads = re.findall(r"<h3>(.*?)</h3>", art, re.S)
    nav = re.search(r"<nav>(.*?)<br/>", art, re.S)
    main = re.search(r"</nav>\s*<ul>(.*?)</ul>", art, re.S)
    items = [text(li) for li in re.findall(r"<li>(.*?)</li>", main.group(1), re.S)] if main else []
    sections = {}
    for m in re.finditer(r"<h3>(.*?)</h3>\s*<ul>(.*?)</ul>", art, re.S):
        sections[text(m.group(1))] = [x for x in (text(li) for li in re.findall(r"<li>(.*?)</li>", m.group(2), re.S))
                                      if x]
    return {"heading": text(heads[0]) if heads else "", "citation": text(nav.group(1)) if nav else "",
            "items": [i for i in items if i], "sections": sections}


def year(s):
    m = re.search(r"\b(1[0-9]{3})\b", s or "")
    return m.group(1) if m else None


def generate(run):
    t, voc, beacon = set(), set(), set()
    entries, unknown = {}, Counter()
    with tarfile.open(run.input("pages"), "r:gz") as tar:
        for m in tar.getmembers():
            if not m.isfile():
                continue
            page = tar.extractfile(m).read().decode("utf-8", errors="replace")
            if NO_ENTRY in page:
                continue
            entries[int(re.search(r"(\d+)\.html$", m.name).group(1))] = parse(page)
    birth, death, label_of = {}, {}, {}
    for n, e in sorted(entries.items()):
        r = IRI(BHR + str(n))
        t.add((r, IRI(RDF_TYPE), IRI(FOAF + "Person")))
        t.add((r, IRI(JLO + "describedAt"), IRI(PAGE + str(n))))
        t.add((r, IRI(RDFS + "label"), Literal(e["heading"])))
        pref, variants = names(e["heading"])
        label_of[n] = pref
        t.add((r, IRI(SKOS + "prefLabel"), Literal(pref)))
        for v in variants:
            t.add((r, IRI(SKOS + "altLabel"), Literal(v)))
        if e["citation"]:
            t.add((r, IRI(DCT + "bibliographicCitation"), Literal(e["citation"])))
        if run.params["rabbi"]:
            t.add((r, IRI(JLO + "occupationURI"), IRI(RABBI)))
        bio = []
        for item in e["items"]:
            for word, which, store in (("Geb.", "birth", birth), ("Gest.", "death", death)):
                if item.startswith(word):
                    date, place = life(item, word)
                    if date:
                        t.add((r, IRI(JLO + which + "Date"), Literal(date)))
                        store[n] = date
                    if place:
                        t.add((r, IRI(JLO + which + "Location"), Literal(place)))
                    break
            else:
                bio.append(item)
        if bio:
            t.add((r, IRI(JLO + "hasAbstract"), Literal("\n".join(bio))))
        for head, items in e["sections"].items():
            prop = next((p for h, p, _en, _de in SECTIONS if h == head), None)
            if prop is None:
                unknown[head] += 1
                continue
            for x in items:
                t.add((r, IRI(VOCAB + prop), Literal(x)))
                if head in AS_PUBLICATION:
                    t.add((r, IRI(JLO + "hasPublication"), Literal(x)))
    for h, p, en, de in SECTIONS:
        voc |= {(IRI(VOCAB + p), IRI(RDF_TYPE), IRI(PREFIXES["rdf"] + "Property")),
                (IRI(VOCAB + p), IRI(RDFS + "label"), Literal(en, None, "en")),
                (IRI(VOCAB + p), IRI(RDFS + "label"), Literal(de, None, "de")),
                (IRI(VOCAB + p), IRI(RDFS + "comment"), Literal(
                    f"A text of the section “{h}” of an entry of the Biographisches Portal der Rabbiner, as "
                    "the portal gives it.", None, "en")),
                (IRI(VOCAB + p), IRI(RDFS + "domain"), IRI(FOAF + "Person")),
                (IRI(VOCAB + p), IRI(RDFS + "range"), IRI(RDFS + "Literal"))}

    # the BEACON: the GND number of an entry (the page of the number names it)
    page_of_gnd = {}
    with tarfile.open(run.input("pages"), "r:gz") as tar:
        for m in tar.getmembers():
            if m.isfile():
                page = tar.extractfile(m).read().decode("utf-8", errors="replace")
                aside = page[page.find("<aside>"):page.find("</aside>")]
                for g in set(re.findall(r"d-nb\.info/gnd/([0-9X-]+)", aside)):
                    page_of_gnd.setdefault(g, set()).add(int(re.search(r"(\d+)\.html$", m.name).group(1)))
    listed = [line.strip() for line in open(run.input("beacon"), encoding="utf-8")
              if line.strip() and not line.startswith("#")]
    no_page = []
    for g in listed:
        ids = page_of_gnd.get(g, set())
        if len(ids) == 1:
            beacon.add((IRI(BHR + str(next(iter(ids)))), IRI(OWL + "sameAs"), IRI("https://d-nb.info/gnd/" + g)))
        else:
            no_page.append(g)

    # replacements of the records of 2026-10-12
    old_ids, old_label, old_years = defaultdict(set), {}, {}
    for s, p, o in run.triples("previous"):
        if not s.startswith(BHR):
            continue
        if p == JLO + "describedAt" and isinstance(o, Literal):
            m = re.search(r"id:(\d+)", o.value)
            if m:
                old_ids[s].add(int(m.group(1)))
        elif p == SKOS + "prefLabel" and isinstance(o, Literal):
            old_label[s] = o.value
        elif p in (JLO + "birthDate", JLO + "deathDate") and isinstance(o, Literal):
            old_years.setdefault(s, {})[p.rsplit("/", 1)[1][:5]] = year(o.value)
    key = lambda s: re.sub(r"\s+", " ", s).strip().lower()  # noqa: E731
    by_label = defaultdict(set)
    for n, lab in label_of.items():
        by_label[key(lab)].add(n)
    stats, how = Counter(), []
    for s in sorted(set(old_label) | set(old_ids)):
        targets = {n for n in old_ids.get(s, set()) if n in entries}
        if old_ids.get(s) and not targets:
            stats["id no longer in the portal"] += 1
        if not old_ids.get(s):
            cand = by_label.get(key(old_label.get(s, "")), set())
            ys = old_years.get(s, {})
            cand = {n for n in cand if (not ys.get("birth") or not year(birth.get(n)) or ys["birth"] == year(birth.get(n)))
                    and (not ys.get("death") or not year(death.get(n)) or ys["death"] == year(death.get(n)))}
            if len(cand) == 1:
                targets = cand
                stats["without id: by name"] += 1
            else:
                stats[f"without id: {'no' if not cand else 'several'} record of that name"] += 1
                how.append(f"{s[len(BHR):]}: {len(cand)} candidates")
        else:
            stats["by id"] += 1
        if len(targets) > 1:
            stats["replaced by several"] += 1
        for n in targets:
            t.add((IRI(s), IRI(DCT + "isReplacedBy"), IRI(BHR + str(n))))
        if not targets:   # no successor: deprecated (decided 2026-10-16; whoever has the IRI looks up the entry)
            t.add((IRI(s), IRI(PREFIXES["owl"] + "deprecated"), Literal("true", XSD_BOOLEAN)))
            stats["deprecated without successor"] += 1
    for line in how:
        run.log("old record not replaced:", line)
    if unknown:
        run.log("sections not known:", dict(unknown))
    for g in no_page:
        run.log("BEACON number without exactly one page:", g)
    run.note(f"{len(entries):,} entries; BEACON {len(listed)} GND numbers, {len(beacon)} linked; records of 2026-10-12: "
             + ", ".join(f"{k} {v:,}" for k, v in sorted(stats.items())) + ".")
    run.write_turtle("bhr.ttl.gz", set(canonical_triples(t)))
    run.write_turtle("bhr-beacon.ttl.gz", set(canonical_triples(beacon)))
    run.write_turtle("bhr-vocabulary.ttl.gz", voc)
