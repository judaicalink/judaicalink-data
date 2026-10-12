"""corrections-links: corrections of identity links (kind correction, decision 0023).

Single findings (0024) from the check of the entity-page closure of 2026-10-12 (decision 0022): links that join
different persons or places. Each block names the dataset, the triples deleted and the evidence; the generator checks
that every deleted triple is in the stable version of its dataset (a correction that no longer applies stops the run)
and that no added triple is there already. Deletions: corrections-links-deletions.ru.gz (SPARQL Update, applied after
all other datasets); additions: corrections-links.ttl.gz.
"""

from jl import corrections
from jl.generator import GeneratorError
from jl.rdf import IRI, RDF_TYPE, Literal
from jl.turtle import PREFIXES

INPUTS = {
    "interlinks": "interlinks/2018-07-18",
    "dbpedia_persons": "dbpedia-persons/2018-10-24",
    "gnd_persons": "gnd-persons/2018-11-29",
    "ubffm_persons": "ubffm-persons/2019-01-24",
    "hhkeydocs": "hhkeydocs/2025-03-21",
    "nli_records": "nli-records/2026-10-12",
    "ls_nli_legacy": "ls-nli-legacy/2026-10-12",
    "dbp_wiki_geo_linking": "dbp-wiki-geo-linking/2021-01-13",
    "rujen": "rujen/2020-09-28",
    "cm_entities": "cm-entities/2026-10-12/cm-entities-wikidata.ttl.gz",
}
PARAMS = {}

J = "http://data.judaicalink.org/data/"
JLO = PREFIXES["jl"]
SAME = PREFIXES["owl"] + "sameAs"
GNDID = "http://d-nb.info/standards/elementset/gnd#gndIdentifier"
LC = "http://id.loc.gov/authorities/names/"


def same(subject, *objects):
    return [(J + subject, SAME, o) for o in objects]


def gnd_numbers(subject, number):
    """gndo:gndIdentifier as a literal and as an IRI (dbpedia-persons states both)."""
    return [(J + subject, GNDID, Literal(number)), (J + subject, GNDID, "http://d-nb.info/gnd/" + number)]


# (input, comment lines, deleted triples, added triples)
CORRECTIONS = [
    ("interlinks", [
        "interlinks: the two Samuel Kohn of bhr are not the Hungarian rabbi Sámuel Kohn (1841-1920, Q7411927): bhr id 957",
        "was vice-rabbi in Bayreuth in the 18th century, id 958 died in 1811 in Tachau; nor are they the same person.",
    ], [t for s in ("bhr/Kohn_Samuel", "bhr/Kohn_Samuel-1") for t in same(
        s, "http://data.judaicalink.org/data/dbpedia/Samuel_Kohn", "http://dbpedia.org/resource/Samuel_Kohn",
        "http://rdf.freebase.com/ns/m.0j677bx", "http://viaf.org/viaf/71441395",
        "http://wikidata.dbpedia.org/resource/Q7411927", "http://www.wikidata.org/entity/Q7411927",
        "http://yago-knowledge.org/resource/Samuel_Kohn")]
        + same("bhr/Kohn_Samuel", J + "bhr/Kohn_Samuel-1") + same("bhr/Kohn_Samuel-1", J + "bhr/Kohn_Samuel")
        + same("dbpedia/Samuel_Kohn", J + "bhr/Kohn_Samuel", J + "bhr/Kohn_Samuel-1",
               "http://steinheim-institut.de:50580/cgi-bin/bhr?id=957",
               "http://steinheim-institut.de:50580/cgi-bin/bhr?id=958"), []),
    ("dbpedia_persons", [
        "dbpedia-persons: Menahem ben Moshe Bavli (Q6816418) carries the identifiers of Menahem Recanati (GND 122534107,",
        "of which 119759152 is a former number; VIAF 101087390, LC nr93011812, Q186452).",
    ], same("dbpedia/Menahem_ben_Moshe_Bavli", "http://d-nb.info/gnd/119759152",
            "http://catalogue.bnf.fr/ark:/12148/cb14513198b", "http://d-nb.info/gnd/122534107/about",
            "http://hub.culturegraph.org/entityfacts/119759152", "http://id.loc.gov/authorities/nr93011812",
            "http://viaf.org/viaf/101087390", "http://www.isni.org/000000009418973X",
            "http://www.wikidata.org/entity/Q186452", "https://de.wikipedia.org/wiki/Menachem_ben_Benjamin_Recanati",
            "https://en.wikipedia.org/wiki/Menahem_Recanati",
            "https://www.deutsche-digitale-bibliothek.de/entity/122534107")
        + gnd_numbers("dbpedia/Menahem_ben_Moshe_Bavli", "119759152"), []),
    ("dbpedia_persons", [
        "dbpedia-persons: Simeon ben Gamliel II (Q1400135) carries the identifiers of Simeon bar Yochai (GND 124813631,",
        "VIAF 10789306, LC n85120027: the NLI record of Simeon bar Yochai has both).",
    ], same("dbpedia/Simeon_ben_Gamliel_II", "http://d-nb.info/gnd/124813631",
            "http://catalogue.bnf.fr/ark:/12148/cb12067142k", "http://d-nb.info/gnd/124813631/about",
            "http://hub.culturegraph.org/entityfacts/124813631", "http://id.loc.gov/authorities/n85120027",
            "http://viaf.org/viaf/10789306", "http://www.isni.org/0000000458756601",
            "https://www.deutsche-digitale-bibliothek.de/entity/124813631")
        + gnd_numbers("dbpedia/Simeon_ben_Gamliel_II", "124813631"), []),
    ("gnd_persons", [
        "gnd-persons (EntityFacts): GND 124813631 is Simeon bar Yochai; the links to Simeon ben Gamliel II are wrong.",
    ], same("gnd/124813631", "http://www.wikidata.org/entity/Q1400135",
            "https://de.wikipedia.org/wiki/Simeon_ben_Gamaliel_II.", "https://en.wikipedia.org/wiki/Simeon_ben_Gamliel_II"),
        []),
    ("dbpedia_persons", [
        "dbpedia-persons: Freebase m.05cv47 is Abraham ben David of Posquières (Q330769), not Abraham ibn Daud (Q330821).",
    ], same("dbpedia/Abraham_ibn_Daud", "http://rdf.freebase.com/ns/m.05cv47"), []),
    ("gnd_persons", [
        "gnd-persons: Sherira Gaon (GND 119169053, Q356149) is not his son Hai Gaon (Q982194).",
    ], same("gnd/119169053", "http://dbpedia.org/resource/Hai_Gaon"), []),
    ("ubffm_persons", [
        "ubffm-persons: the same link for Sherira Gaon.",
    ], same("ubffm/Šerîrâ_Gāôn", "http://dbpedia.org/resource/Hai_Gaon"), []),
    ("hhkeydocs", [
        "hhkeydocs: Otto Warburg (1859-1938, botanist, GND 117565725) is not the physiologist Otto Heinrich Warburg",
        "(1883-1970, GND 118629158, VIAF 112658460).",
    ], [(J + "hhkeydocs/Otto_Warburg", GNDID, Literal("118629158"))]
        + same("hhkeydocs/Otto_Warburg", "https://viaf.org/viaf/http://viaf.org/viaf/112658460/"), []),
    ("hhkeydocs", [
        "hhkeydocs: Kurt Singer (1885-1944, neurologist and musicologist, GND 117402362) is not the philosopher Kurt Singer",
        "(1886-1962, GND 120639734, VIAF 59920664).",
    ], [(J + "hhkeydocs/Kurt_Singer", GNDID, Literal("120639734"))]
        + same("hhkeydocs/Kurt_Singer", "https://viaf.org/viaf/http://viaf.org/viaf/59920664/"), []),
    ("nli_records", [
        "nli-records: LC n2008069970 is Nili Goren (Lieneke, 1933-; id.loc.gov), not Jacob van der Hoeden;",
        "LC n82018212 is the photographer Stefan Moses, not Stéphane Mosès; LC n82089580 is the work Goethe, Faust",
        "(a name-title), not Goethe.",
    ], same("nli/record/viaf-289600534", LC + "n2008069970") + same("nli/record/viaf-54349072", LC + "n82018212")
        + same("nli/record/viaf-24602065", LC + "n82089580"), []),
    ("ls_nli_legacy", [
        "ls-nli-legacy: the same LC numbers on the legacy URIs of these records.",
    ], same("nli/VanDerHoeden_Jaacob", LC + "n2008069970") + same("nli/Mosès_Stéphane_", LC + "n82018212")
        + [t for u in ("nli/Goethe_JohannWolfgangvon_", "nli/Goethe_JohannWolfgangvon_1", "nli/Goethe_JohannWolfgangvon_12",
                       "nli/גתה_יוהןוולפגנג_") for t in same(u, LC + "n82089580")], []),
    ("nli_records", [
        "nli-records: works (name-title records) carrying the LC number of their author, a personal name (id.loc.gov):",
        "Ahimaaz ben Paltiel, C. S. Lewis, Tzvi Avni, Aharon Almog, Avigdor Dagan (Viktor Fischl), Solomon Small,",
        "Yehoshue Perle.",
    ], same("nli/record/viaf-311794351", LC + "n2001041900") + same("nli/record/viaf-179642103", LC + "n79003974")
        + same("nli/record/viaf-242350032", LC + "n79100200")
        + same("nli/record/viaf-4975148269815005230004", LC + "n84182018")
        + same("nli/record/viaf-308552496", LC + "n85813504") + same("nli/record/viaf-56213280", LC + "no97016740")
        + same("nli/record/viaf-154146462665727771679", LC + "nr91021404"), []),
    ("cm_entities", [
        "cm-entities: VIAF 308556423 is the work Meshal ha-kadmoni (NLI), not its author Isaac ben Solomon Sahula",
        "(taken over from Wikidata Q61126269, which has both).",
    ], same("dbpedia/Isaak_ben_Salomo_Sahula", "http://viaf.org/viaf/308556423"), []),
    ("dbp_wiki_geo_linking", [
        "dbp-wiki-geo-linking: links to disambiguation pages of the Russian Wikipedia, which name several places",
        "(Granada and Grenada were joined through one of them).",
    ], same("Cleveland,Ohio", "http://ru.wikipedia.org/wiki/Кливленд_(значения)")
        + same("Durham", "http://ru.wikipedia.org/wiki/Дарем_(значения)")
        + same("Granada", "http://ru.wikipedia.org/wiki/Гренада_(значения)")
        + same("Limerick", "http://ru.wikipedia.org/wiki/Лимерик_(значения)")
        + same("geonames/3580239", "http://ru.wikipedia.org/wiki/Гренада_(значения)"), []),
    ("rujen", [
        "rujen: Marseille, Berlin and Lviv are places, typed as persons.",
    ], [(J + f"rujen/{x}", RDF_TYPE, JLO + "Person") for x in ("marselj", "berlin", "ljvov")],
        [(J + f"rujen/{x}", RDF_TYPE, JLO + "Place") for x in ("marselj", "berlin", "ljvov")]),
]


def term(x):
    return x if isinstance(x, Literal) else IRI(x)


def generate(run):
    by_input = {}
    for name, _c, deleted, added in CORRECTIONS:
        by_input.setdefault(name, set()).update(corrections.key(tuple(map(term, t))) for t in deleted + added)
    found = {}
    for name, wanted in by_input.items():
        found[name] = {k for k in map(corrections.key, run.triples(name)) if k in wanted}
    blocks, additions, problems = [], set(), []
    for name, comments, deleted, added in CORRECTIONS:
        ts = [tuple(map(term, t)) for t in deleted]
        problems += [f"{name}: not in its version, nothing to delete: {t}" for t in ts
                     if corrections.key(t) not in found[name]]
        adds = [tuple(map(term, t)) for t in added]
        problems += [f"{name}: already in its version, nothing to add: {t}" for t in adds
                     if corrections.key(t) in found[name]]
        blocks.append((comments, ts))
        additions.update(adds)
    if problems:
        raise GeneratorError("corrections that do not apply:\n" + "\n".join(problems))
    n = sum(len(b[1]) for b in blocks)
    run.note(f"{n} triples deleted in {len({c[0] for c in CORRECTIONS})} datasets, {len(additions)} added.")
    run.write_deletions("corrections-links-deletions.ru.gz", blocks)
    run.write_turtle("corrections-links.ttl.gz", additions)
