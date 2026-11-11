"""Normalised dates (decision 0035): xsd:date, xsd:gYearMonth or xsd:gYear where the value is one day, month or year,
else the EDTF value typed with the datatype of the Library of Congress.

normalised(edtf) takes an EDTF value as a source writes it (the LC specification of 2012, which Footprints uses:
"1778~", "1555/1631", "177x", "unknown/1750", "uuuu-uu-12"; and the ISO 8601-2 forms "177X", "../1750", seasons
"1810-23") and gives the
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
    if len(parts) == 2 and parts[1].isdigit() and 21 <= int(parts[1]) <= 24:   # a season: 1810-23 (autumn)
        return True
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
    if re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", v) and v[:4] != "0000":   # a month (21-24 are EDTF seasons)
        return Literal(v, XSD + "gYearMonth")
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", v) and _valid(v) and v[:4] != "0000":
        return Literal(v, XSD + "date")
    return Literal(v, EDTF) if is_edtf(v) else None


# --- the Hebrew calendar (Reingold and Dershowitz, Calendrical Calculations; days as Python ordinals) --------------

HEBREW_EPOCH = -1373427   # 1 Tishri 1 AM: 7 October 3761 BCE (Julian) as a proleptic Gregorian ordinal
# months numbered as in Calendrical Calculations: 1 Nisan … 6 Elul, 7 Tishri … 12 Adar (Adar I in a leap year), 13 Adar II
HEBREW_MONTHS = {
    "nisan": 1, "nissan": 1, "ijar": 2, "ijjar": 2, "iyar": 2, "iyyar": 2, "siwan": 3, "sivan": 3, "tammus": 4,
    "tamus": 4, "tammuz": 4, "tamuz": 4, "ab": 5, "av": 5, "aw": 5, "elul": 6, "tischri": 7, "tishri": 7, "tishrei": 7,
    "cheschwan": 8, "marcheschwan": 8, "cheshvan": 8, "heshvan": 8, "marheshvan": 8, "kislew": 9, "kislev": 9,
    "tewet": 10, "tevet": 10, "tebeth": 10, "tebet": 10, "schewat": 11, "schebat": 11, "shevat": 11, "shvat": 11,
    "adar": 12, "adar i": 12, "adar rischon": 12, "adar ii": 13, "adar scheni": 13, "weadar": 13, "veadar": 13,
}


def hebrew_leap(year):
    return (7 * year + 1) % 19 < 7


def _elapsed(year):
    months = (235 * year - 234) // 19
    parts = 12084 + 13753 * months
    day = 29 * months + parts // 25920
    return day + 1 if (3 * (day + 1)) % 7 < 3 else day


def _new_year(year):
    ny0, ny1, ny2 = _elapsed(year - 1), _elapsed(year), _elapsed(year + 1)
    correction = 2 if ny2 - ny1 == 356 else 1 if ny1 - ny0 == 382 else 0
    return HEBREW_EPOCH + ny1 + correction


def hebrew_month_days(year, month):
    length = _new_year(year + 1) - _new_year(year)
    if month in (2, 4, 6, 10, 13) or (month == 12 and not hebrew_leap(year)):
        return 29
    if month == 8 and length % 10 != 5:   # Marcheschwan is long only in years of 355 or 385 days
        return 29
    if month == 9 and length % 10 == 3:   # Kislew is short in years of 353 or 383 days
        return 29
    return 30


def hebrew_to_gregorian(year, month, day):
    """A Hebrew date (year AM, month as in HEBREW_MONTHS, day) as datetime.date, or None if the day does not exist."""
    last = 13 if hebrew_leap(year) else 12
    if not (1 <= month <= last and 1 <= day <= hebrew_month_days(year, month)):
        return None
    days = _new_year(year) + day - 1
    if month < 7:
        days += sum(hebrew_month_days(year, m) for m in range(7, last + 1))
        days += sum(hebrew_month_days(year, m) for m in range(1, month))
    else:
        days += sum(hebrew_month_days(year, m) for m in range(7, month))
    return datetime.date.fromordinal(days)
