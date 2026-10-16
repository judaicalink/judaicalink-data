"""Place names to GeoNames ids, offline and deterministic, from the GeoNames dump (inputs:geonames/dump-<date>).

A place text from a record (e.g. "Arad (Rumänien)", "Lissa", "Boston, Mass.") is cleaned into a name and an optional
qualifier (the text in parentheses or after a comma). Texts with a question mark (uncertain in the source) and
placeholders are left out. The whole cleaned text is looked up first ("Frankfurt (Oder)" is a GeoNames name); only if
it has no candidate, the name without the qualifier.

Candidates are the populated places (feature class P, including city districts), administrative units (class A) and
regions (RGN, RGNH: Böhmen, Galizien) that have the name (compared case-insensitively) in one of two tiers:
1. as their name or ASCII name, or as an alternate name in a language (exonyms such as Lissa for Leszno, Birnbaum
   for Międzychód, Klausenburg for Cluj-Napoca);
2. as an alternate name without a language;
never as a code (airport, postal, link, abbreviation) or a colloquial name. Only the candidates of the first tier
that has any are considered.

A qualifier keeps the candidates it fits: those whose country, first- or second-level division it names (for the
United States also the state abbreviations, "Calif.", "NY"), or else those within CLUSTER_KM of a populated place or
administrative unit of that name, or else those within REGION_KM of a region of that name (Schlesien, Mähren,
Galizien), or of a city of that name (PROVINCE_POP inhabitants) if there is no such region (Posen for the
province); names are compared also without a leading "Landkreis", "Kanton", "Departement" etc.; "Stadt" or "City"
keeps the populated places. A qualifier that names something known but fits no candidate leaves the text out
("Prerau (Mähren)" is not the Preraū of Nepal); one that names nothing known, a river or a part of a city is ignored
("Naumburg (Saale)", "Berlin (Ost)").

The best candidate is the one with the largest population; only populated places count with their population
(countries, divisions, regions and city districts stand for an area or a part and count as 0). Candidates within
CLUSTER_KM of it in the same country are the same place in another form (Berlin the city and Berlin the state, a town
and its district) and do not compete (a region is never the same place as another candidate); of them, the populated
place with the largest population is taken. The best candidate is taken if no other candidate is left, or if its
population is at least RATIO times that of every other one, where a population below MIN_POP (GeoNames gives 0 for
unknown) counts as MIN_POP; otherwise the name is ambiguous and left out.
"""

import io
import math
import re
import unicodedata
import zipfile

CLUSTER_KM = 30
REGION_KM = 250
PROVINCE_POP = 100000
# qualifiers that are no place: parts of a city, kinds of places
QUALIFIER_IGNORED = {"ost", "west", "nord", "süd", "region", "seebad", "kurort", "dorf", "gut", "land"}
RATIO = 10
MIN_POP = 1000
NOT_NAMES = {"link", "wkdt", "post", "iata", "icao", "faac", "abbr", "unlc", "tcid", "fr_1793", "phon"}
# the United States: postal codes and the abbreviations of the AP style, as qualifiers ("Boston, Mass.")
US_STATES = {k.replace(".", ""): v for v, ks in {
    "AL": "ala. al", "AK": "alaska ak", "AZ": "ariz. az", "AR": "ark. ar", "CA": "calif. cal. ca", "CO": "colo. co",
    "CT": "conn. ct", "DE": "del. de", "DC": "d.c. dc", "FL": "fla. fl", "GA": "ga. ga", "HI": "hawaii hi",
    "ID": "idaho id", "IL": "ill. il", "IN": "ind. in", "IA": "iowa ia", "KS": "kan. kans. ks", "KY": "ky. ky",
    "LA": "la. la", "ME": "maine me", "MD": "md. md", "MA": "mass. ma", "MI": "mich. mi", "MN": "minn. mn",
    "MS": "miss. ms", "MO": "mo. mo", "MT": "mont. mt", "NE": "neb. nebr. ne", "NV": "nev. nv", "NH": "n.h. nh",
    "NJ": "n.j. nj", "NM": "n.m. nm", "NY": "n.y. ny", "NC": "n.c. nc", "ND": "n.d. nd", "OH": "ohio oh",
    "OK": "okla. ok", "OR": "ore. or", "PA": "pa. pa", "RI": "r.i. ri", "SC": "s.c. sc", "SD": "s.d. sd",
    "TN": "tenn. tn", "TX": "tex. tx", "UT": "utah ut", "VT": "vt. vt", "VA": "va. va", "WA": "wash. wa",
    "WV": "w.va. wv", "WI": "wis. wi", "WY": "wyo. wy"}.items() for k in ks.split()}
# words that name the kind of a division in a qualifier ("Landkreis Starnberg", "Departement Alpes-Maritimes")
UNIT_WORDS = (r"^(?:landkreis|kreis|bezirk|regierungsbezirk|kanton|departement|département|provinz|woiwodschaft|"
              r"gouvernement|komitat|region|county) ")
PLACEHOLDERS = {"", "nn", "n.n.", "unbekannt", "unknown", "-"}


def key(s):
    return unicodedata.normalize("NFC", s).casefold().strip()


def normal(literal):
    # U+031C (combining left half ring below) stands for the ogonek in some GND names: "Be̜dzin", "Warta̜"
    s = unicodedata.normalize("NFC", literal.replace("\u031c", "\u0328")).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip().strip(" .;:-")


def clean(literal):
    """(name, qualifier or None), or (None, reason)."""
    s = normal(literal)
    if "?" in s:
        return None, "uncertain (?)"
    qualifier = None
    m = re.match(r"^([^(),]+?)\s*\(\s*([^()]*?)\s*\)\s*$", s)
    if m:
        s, qualifier = m.group(1), m.group(2) or None
    elif "," in s:
        s, _, q = s.partition(",")
        qualifier = q.strip() or None
    s = s.strip(" .;:-")
    if key(s) in PLACEHOLDERS:
        return None, "placeholder"
    return s, qualifier


def pop(r):
    """The population that counts: that of a populated place; countries, divisions and city districts stand for an
    area or a part, so their population is not compared with that of places."""
    return r["pop"] if r["class"] == "P" and r["code"] != "PPLX" else 0


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(min(1.0, h)))


class Gazetteer:
    """The candidates for a set of names (and qualifiers), read from the dump once."""

    def __init__(self, all_countries, alternate_names, names, qualifiers=()):
        wanted = {key(n) for n in names}
        wanted_q = {key(q) for q in qualifiers} | {re.sub(UNIT_WORDS, "", key(q)) for q in qualifiers}
        # tiers of the alternate names: (name key, GeoNames id) -> best tier
        alt_tier = {}
        with zipfile.ZipFile(alternate_names) as z, z.open("alternateNamesV2.txt") as f:
            for row in io.TextIOWrapper(f, encoding="utf-8"):
                c = row.rstrip("\n").split("\t")
                k = key(c[3])
                if k not in wanted or c[2] in NOT_NAMES or (len(c) > 6 and c[6] == "1"):
                    continue
                tier = 2 if c[2] == "" else 1
                if alt_tier.get((k, c[1]), 3) > tier:
                    alt_tier[(k, c[1])] = tier
        alt_ids = {}
        for (k, gid), tier in alt_tier.items():
            alt_ids.setdefault(gid, []).append((k, tier))
        self.cands = {k: [] for k in wanted}
        self.region_names = {}   # ("cc", cc) / ("a1", cc, admin1) / ("a2", cc, admin1, admin2) -> names
        self.qualifier_points = {k: [] for k in wanted_q}   # qualifier key -> coordinates of places of that name
        self.qualifier_regions = {k: [] for k in wanted_q}  # qualifier key -> coordinates of regions of that name
        self.rivers = set()                                  # qualifiers that name a stream
        with zipfile.ZipFile(all_countries) as z, z.open("allCountries.txt") as f:
            for row in io.TextIOWrapper(f, encoding="utf-8"):
                c = row.rstrip("\n").split("\t")
                fclass, fcode = c[6], c[7]
                if fcode in ("STM", "STMH"):
                    self.rivers.update(({key(c[1]), key(c[2])} | {key(a) for a in c[3].split(",") if a}) & wanted_q)
                if fclass not in ("P", "A") and fcode not in ("RGN", "RGNH"):
                    continue
                own = {key(c[1]), key(c[2])}
                all_names = own | {key(a) for a in c[3].split(",") if a}
                if fclass == "L":
                    for k in all_names & wanted_q:
                        self.qualifier_regions[k].append((float(c[4]), float(c[5])))
                if fclass == "A":
                    region = (("cc", c[8]) if fcode.startswith("PCL") else ("a1", c[8], c[10]) if fcode == "ADM1"
                              else ("a2", c[8], c[10], c[11]) if fcode == "ADM2" else None)
                    if region:
                        self.region_names.setdefault(region, set()).update(all_names)
                for k in all_names & wanted_q if fclass != "L" else ():
                    self.qualifier_points[k].append((float(c[4]), float(c[5]), int(c[14] or 0)))
                tiers = {k: 1 for k in own & wanted}
                for k, tier in alt_ids.get(c[0], ()):
                    tiers[k] = min(tier, tiers.get(k, 3))
                if not tiers:
                    continue
                rec = {"id": c[0], "name": c[1], "class": fclass, "code": fcode, "cc": c[8], "admin1": c[10],
                       "admin2": c[11], "pop": int(c[14] or 0), "lat": float(c[4]), "lng": float(c[5])}
                for k, tier in tiers.items():
                    self.cands[k].append(dict(rec, tier=tier))

    def qualified(self, cands, qualifier):
        """(the candidates the qualifier fits, whether the qualifier names anything known)."""
        q = key(qualifier)
        if q in ("stadt", "city"):
            return [r for r in cands if r["class"] == "P"], True
        state = US_STATES.get(q.replace(" ", "").replace(".", ""))
        if state:
            return [r for r in cands if r["cc"] == "US" and r["admin1"] == state], True
        qs = {q, re.sub(UNIT_WORDS, "", q)}
        if qs & QUALIFIER_IGNORED or qs & self.rivers:
            return [], False
        in_region = [r for r in cands if any(
            qs & self.region_names.get(x, set())
            for x in (("cc", r["cc"]), ("a1", r["cc"], r["admin1"]), ("a2", r["cc"], r["admin1"], r["admin2"])))]
        if in_region:
            return in_region, True
        points = [p for x in qs for p in self.qualifier_points.get(x, ())]
        near = [r for r in cands if any(km(p[:2], (r["lat"], r["lng"])) <= CLUSTER_KM for p in points)]
        if near:
            return near, True
        regions = ([p for x in qs for p in self.qualifier_regions.get(x, ())]
                   or [p[:2] for p in points if p[2] >= PROVINCE_POP])   # a city for its province (Posen)
        inside = [r for r in cands if any(km(p, (r["lat"], r["lng"])) <= REGION_KM for p in regions)]
        return inside, bool(points or regions or any(qs & names for names in self.region_names.values()))

    def choose_text(self, literal):
        """(GeoNames record or None, how) for a place text: the whole text, else its name and qualifier."""
        name, qualifier = clean(literal)
        if name is None:
            return None, qualifier
        if self.cands.get(key(normal(literal))):
            return self.choose(normal(literal))
        return self.choose(name, qualifier)

    def choose(self, name, qualifier=None):
        """(GeoNames record or None, how)."""
        cands = self.cands.get(key(name), [])
        if not cands:
            return None, "no candidate"
        tier = min(r["tier"] for r in cands)
        cands = [r for r in cands if r["tier"] == tier]
        how = "name" if tier == 1 else "alternate name without language"
        if qualifier:
            q, known = self.qualified(cands, qualifier)
            if q:
                cands, how = q, how + " and qualifier"
            elif known:
                return None, "qualifier fits no candidate"
        cands = sorted(cands, key=lambda r: (-pop(r), r["class"] != "P", int(r["id"])))
        best = cands[0]
        cluster = [r for r in cands if r is best or (
            r["class"] != "L" and best["class"] != "L" and r["cc"] == best["cc"]
            and km((r["lat"], r["lng"]), (best["lat"], best["lng"])) <= CLUSTER_KM)]
        others = [r for r in cands if r not in cluster]
        places = [r for r in cluster if r["class"] == "P"]
        chosen = places[0] if places else best
        if not others:
            return chosen, how
        if pop(best) >= RATIO * max(max(pop(r), MIN_POP) for r in others):
            return chosen, how + ", by population"
        return None, f"ambiguous ({len(others) + 1} places)"
