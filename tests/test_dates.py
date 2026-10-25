"""Tests of the normalised dates (decision 0035): python3 -m unittest (repository root)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jl.dates import EDTF, normalised  # noqa: E402
from jl.rdf import XSD  # noqa: E402


class Normalised(unittest.TestCase):
    def test_xsd(self):
        self.assertEqual(normalised("1778"), (("1778", XSD + "gYear", None)))
        self.assertEqual(normalised("1778-05").datatype, XSD + "gYearMonth")
        self.assertEqual(normalised(" 1778-05-03 ").datatype, XSD + "date")

    def test_edtf(self):
        for v in ("1778~", "1555/1631", "177x", "99xx", "unknown/1750", "1750?~/1760?~", "uuuu-uu-12", "177X",
                  "../1750", "1778-05-03~"):
            self.assertEqual(normalised(v).datatype, EDTF, v)

    def test_not_a_date(self):
        for v in ("o", "9", "1631-1640", "unknown/unknown", "1778-02-30", "2000-13", "", None):
            self.assertIsNone(normalised(v), v)


if __name__ == "__main__":
    unittest.main()
