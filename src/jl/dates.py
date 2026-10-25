"""Normalised dates (decision 0035): xsd:date, xsd:gYearMonth or xsd:gYear where the value is one day, month or year,
else the EDTF value typed with the datatype of the Library of Congress.

normalised(edtf) takes an EDTF value as a source writes it (the LC specification of 2012, which Footprints uses:
"1778~", "1555/1631", "177x", "unknown/1750", "uuuu-uu-12"; and the ISO 8601-2 forms "177X", "../1750") and gives the
typed literal, or None where the value is no EDTF date.
"""

import datetime
import re

from .rdf import XSD, Literal

EDTF = "http://id.loc.gov/datatypes/edtf/EDTF"

_DATE = r"-?[0-9uxX]{4}(?:-[0-9uxX]{2}(?:-[0-9uxX]{2})?)?"
_SINGLE = re.compile(rf"({_DATE})(?:\?~|~\?|\?|~|%)?")
_OPEN = {"unknown", "open", "", ".."}


def _valid(date):
    """The digits of a date are a possible year, month and day (unspecified digits pass)."""
    parts = date.lstrip("-").split("-")
    if len(parts) > 1 and parts[1].isdigit() and not 1 <= int(parts[1]) <= 12:
        return False
    if len(parts) > 2 and parts[2].isdigit() and not 1 <= int(parts[2]) <= 31:
        return False
    if len(parts) == 3 and all(p.isdigit() for p in parts):
        try:
            datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
        except ValueError:
            return False
    return True


def is_edtf(value):
    """A single date or an interval of the forms above."""
    ends = value.split("/")
    if len(ends) == 1:
        m = _SINGLE.fullmatch(value)
        return bool(m) and _valid(m.group(1))
    if len(ends) != 2 or all(e in _OPEN for e in ends):
        return False
    return all(e in _OPEN or ((m := _SINGLE.fullmatch(e)) and _valid(m.group(1))) for e in ends)


def normalised(edtf):
    v = (edtf or "").strip()
    if re.fullmatch(r"[0-9]{4}", v) and v != "0000":
        return Literal(v, XSD + "gYear")
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}", v) and _valid(v) and v[:4] != "0000":
        return Literal(v, XSD + "gYearMonth")
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", v) and _valid(v) and v[:4] != "0000":
        return Literal(v, XSD + "date")
    return Literal(v, EDTF) if is_edtf(v) else None
