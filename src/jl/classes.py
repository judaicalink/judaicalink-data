"""The classes of the entities in our data (the common layer, judaicalink-ontology).

Standard classes since 2026-10-17: jl:Place, jl:Work and jl:Subject are deprecated in favour of schema:Place,
schema:CreativeWork and skos:Concept; data published before keeps them, datasets switch with their next version.
Generators write PERSON, ORGANISATION, PLACE, WORK, SUBJECT; readers use kind() to recognise both forms.
"""

from .turtle import PREFIXES

FOAF, SCHEMA, SKOS, JL = (PREFIXES[p] for p in ("foaf", "schema", "skos", "jl"))

PERSON = FOAF + "Person"
ORGANISATION = FOAF + "Organization"
PLACE = SCHEMA + "Place"
WORK = SCHEMA + "CreativeWork"
SUBJECT = SKOS + "Concept"

# deprecated classes and what replaces them (jl:Person was never defined; rujen used it)
DEPRECATED = {JL + "Place": PLACE, JL + "Work": WORK, JL + "Subject": SUBJECT, JL + "Person": PERSON}

KIND = {PERSON: "Person", ORGANISATION: "Organization", PLACE: "Place", WORK: "Work", SUBJECT: "Subject"}


def current(cls):
    """The class to write for a class (a deprecated one replaced)."""
    return DEPRECATED.get(cls, cls)


def kind(cls):
    """Person, Organization, Place, Work, Subject or None, for the current and the deprecated classes."""
    return KIND.get(current(cls))
