"""Linksets per authority dataset (decision 0029): every record of ours that refers to an authority is linked to our
record of the current authority entry.

authority_linkset(run, source, authority, inputs, prefix) reads the authority dataset (its records <prefix><id>, the
replacements of its identifiers, dcterms:isReplacedBy, and the deprecated ones, owl:deprecated), finds every
reference to the source in the inputs (jl.identifiers: IRIs as objects in any form, identifier literals), resolves it
to the current record and states <record> jl:sameAs <prefix><current id> (a subproperty of owl:sameAs: the identity
as JudaicaLink states it). Only identity statements count (owl:sameAs,
skos:exactMatch, madsrdf:hasExactExternalAuthority, identifier literals): a place of birth or an occupation that is an
authority entry does not make the record that entry. Left out and logged: references to
identifiers that are deprecated or not in the authority dataset, references by blank nodes or by records of the
authority itself, and links whose two sides are of contradicting kinds (a person and a work, a person or a work and
a place: e.g. Wikidata gives a person the LC number of one of his books; an organisation can be a place or a person's
firm). A record that refers to several current entries is linked to each (the entity pages join them, as
before) and listed in the log for review.
"""

from collections import Counter, defaultdict

from . import classes, identifiers
from .rdf import RDF_TYPE, BNode, IRI, Literal
from .turtle import PREFIXES

SAME = PREFIXES["owl"] + "sameAs"
JLSAME = PREFIXES["jl"] + "sameAs"   # identity as JudaicaLink states it (decision 0029)
REPLACED = PREFIXES["dcterms"] + "isReplacedBy"
DEPRECATED = PREFIXES["owl"] + "deprecated"
# the statements that say a record is the authority entry (also Wikidata's identifier properties); other references
# (a place of birth, an occupation) are not
IDENTITY = identifiers.IDENTITY


# kinds that cannot be the same thing (an organisation can be a place, e.g. a city, or a person's firm, e.g. a printer)
CONTRADICTING = {frozenset({"Person", "Work"}), frozenset({"Person", "Place"}), frozenset({"Work", "Place"})}


def kinds(run, names, prefix=identifiers.JL):
    """{record: {Person, Place, Work, Organization, Subject}} from the rdf:type statements of the inputs."""
    out = defaultdict(set)
    for name in names:
        for s, p, o in run.triples(name):
            if p == RDF_TYPE and not isinstance(o, Literal) and str(s).startswith(prefix):
                k = classes.kind(str(o))
                if k:
                    out[str(s)].add(k)
    return out


def contradict(a, b):
    """Whether two sets of kinds cannot belong to the same thing (every pair contradicts)."""
    return bool(a and b) and all(frozenset({x, y}) in CONTRADICTING for x in a for y in b)


def authority_index(run, source, authority):
    """(current ids, {old id: current id}, {deprecated ids}) from the authority dataset."""
    current, to, deprecated = set(), {}, set()
    for s, p, o in run.triples(authority):
        x = identifiers.identify(s)
        if not x or x[0] != source:
            continue
        if p == REPLACED:
            y = identifiers.identify(o)
            if y and y[0] == source:
                to[x[1]] = y[1]
        elif p == DEPRECATED:
            deprecated.add(x[1])
        elif p == SAME and s.startswith(identifiers.JL):
            current.add(x[1])
    for old in list(to):   # follow chains
        seen = {old}
        while to[old] in to and to[old] not in seen:
            seen.add(to[old])
            to[old] = to[to[old]]
    return current, to, deprecated


def authority_linkset(run, source, authority, inputs, prefix, leave_out=None):
    """The links (a set of triples) and writes the counts as a note; see the module docstring. leave_out(record,
    current id): a reason to leave the link out (e.g. contradicting life dates, ls-viaf), or None."""
    current, to, deprecated = authority_index(run, source, authority)
    run.log(f"{authority}: {len(current):,} current records, {len(to):,} replaced identifiers, "
            f"{len(deprecated):,} deprecated")
    kind_of = kinds(run, [authority, *inputs])
    links, targets = set(), defaultdict(set)
    c, by_dataset, left_out = Counter(), Counter(), []
    for name, ref in inputs.items():
        slug = ref.split("/", 1)[0]
        for s, p, o in run.triples(name):
            if p not in IDENTITY:
                continue
            x = identifiers.identify(o, p)
            if not x or x[0] != source:
                continue
            c["references"] += 1
            if isinstance(s, BNode) or not s.startswith(identifiers.JL):
                c["left out: subject not one of our records"] += 1
                continue
            own = identifiers.identify(s)
            if own and own[0] == source:
                c["left out: subject is an authority record"] += 1
                continue
            n = x[1]
            if n in current:
                cur = n
            elif to.get(n) in current:
                cur = to[n]
                c["resolved through a replacement"] += 1
            else:
                why = "deprecated" if n in deprecated else "not in the authority dataset"
                c[f"left out: {why}"] += 1
                left_out.append(f"{s} {n} ({why}, {slug})")
                continue
            why = ("classes contradict" if contradict(kind_of.get(str(s), set()), kind_of.get(prefix + cur, set()))
                   else leave_out(str(s), cur) if leave_out else None)
            if why:
                c[f"left out: {why}"] += 1
                left_out.append(f"{s} {cur} ({why}, {slug})")
                continue
            links.add((IRI(s), IRI(JLSAME), IRI(prefix + cur)))
            targets[s].add(cur)
            by_dataset[slug] += 1
    several = {s: t for s, t in targets.items() if len(t) > 1}
    for s, t in sorted(several.items()):
        run.log(f"several {source} records: {s} -> {', '.join(sorted(t))}")
    for line in sorted(left_out):
        run.log("left out:", line)
    run.note(f"{len(links):,} links of {len(targets):,} records to {len({t for ts in targets.values() for t in ts}):,} "
             f"{source} records; {len(several):,} records with several (log); by dataset: "
             + ", ".join(f"{k} {v:,}" for k, v in by_dataset.most_common()) + "; "
             + ", ".join(f"{k} {v:,}" for k, v in sorted(c.items())) + ".")
    return links
