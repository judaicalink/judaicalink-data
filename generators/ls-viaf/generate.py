"""ls-viaf: every record of ours that refers to a VIAF cluster, linked to our record of the cluster (decision 0029).

References: VIAF numbers (viaf.org/viaf/<n> in any form, our records data/viaf/<n>) in our datasets and the other
authority datasets (jl.authorities.linking_inputs: the stable versions, or the runs of jl generate --use); the rules
are in jl.linksets. VIAF gets the benefit of the doubt (0029); a link is left out when
- the life dates contradict: the record and the cluster both give a year of birth (or of death), and no two of these
  years are within one year of each other (a difference of one year is kept and counted: calendars and conversions
  differ by a year often); the years are the first three- or four-digit numbers of jl:birthDate/jl:deathDate and
  jl:birthDateNormalized/jl:deathDateNormalized (records-normalized), of the record and of the cluster;
- the classes contradict: the cluster is a work (schema:CreativeWork) and the record a person or the other way round
  (e.g. cm-entities takes every VIAF number of a Wikidata item, which can include the cluster of a work).
The dump states no successors of merged clusters, so a number not in the dataset viaf is left out (logged).
"""

import re
from collections import Counter, defaultdict

from jl import authorities, classes
from jl.linksets import authority_linkset
from jl.rdf import RDF_TYPE, Literal
from jl.turtle import PREFIXES

LINKED = authorities.linking_inputs("viaf")   # our datasets and the other authority datasets
INPUTS = {"authority": authorities.authority_input("viaf"), **LINKED}
PARAMS = {}

JL, JLO = "http://data.judaicalink.org/data/", PREFIXES["jl"]
VIAF = JL + "viaf/"
DATES = {JLO + "birthDate": "birth", JLO + "birthDateNormalized": "birth", JLO + "deathDate": "death",
         JLO + "deathDateNormalized": "death"}
YEAR = re.compile(r"(?<!\d)(-?\d{3,4})(?!\d)")
PERSON, WORK = classes.PERSON, classes.WORK


def facts(triples, wanted=None):
    """{subject: {"birth": {years}, "death": {years}, "class": {Person/Work}}}."""
    out = defaultdict(lambda: defaultdict(set))
    for s, p, o in triples:
        if wanted is not None and not wanted(s):
            continue
        if p in DATES and isinstance(o, Literal):
            m = YEAR.search(o.value)
            if m:
                out[str(s)][DATES[p]].add(int(m.group(1)))
        elif p == RDF_TYPE and not isinstance(o, Literal):
            k = classes.kind(str(o))
            if k in ("Person", "Work"):
                out[str(s)]["class"].add(k)
    return out


def generate(run):
    cluster = facts(run.triples("authority"), lambda s: str(s).startswith(VIAF))
    record = defaultdict(lambda: defaultdict(set))
    for name in LINKED:
        for s, f in facts(run.triples(name), lambda s: str(s).startswith(JL)).items():
            for k, v in f.items():
                record[s][k] |= v
    run.log(f"facts: {len(cluster):,} clusters, {len(record):,} records with dates or classes")
    kept_one_year = Counter()

    def leave_out(s, n):
        r, c = record.get(s, {}), cluster.get(VIAF + n, {})
        if r.get("class") and c.get("class") and not (r["class"] & c["class"]):
            return "classes contradict (person and work)"
        for kind in ("birth", "death"):
            a, b = r.get(kind), c.get(kind)
            if a and b:
                d = min(abs(x - y) for x in a for y in b)
                if d > 1:
                    return f"{kind} years contradict"
                if d == 1:
                    kept_one_year[kind] += 1
        return None

    links = authority_linkset(run, "viaf", "authority", LINKED, VIAF, leave_out)
    run.note(f"kept with years one apart: birth {kept_one_year['birth']:,}, death {kept_one_year['death']:,}.")
    run.write_turtle("ls-viaf.ttl.gz", links)
