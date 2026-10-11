"""The values of the catalogue fields kind and method, catalog/vocabulary.toml (decisions 0013, 0018).

Each value is a SKOS concept datasets/vocabulary/<field>/<value> in the scheme datasets/vocabulary/<field>; the
-meta files state them as dcterms:type of the dataset, the dataset judaicalink-vocabulary defines them.
"""

import tomllib

from .config import CATALOG

FIELDS = ("kind", "method")
BASE = "http://data.judaicalink.org/datasets/vocabulary/"


def scheme_iri(field):
    return f"{BASE}{field}"


def value_iri(field, value):
    return f"{BASE}{field}/{value}"


def load(path=None):
    """{field: {"label", "definition", "values": {value: {"label", "definition", ...}}}}; raises ValueError."""
    path = path or CATALOG / "vocabulary.toml"
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as e:
        raise ValueError(f"vocabulary.toml: {e}") from None
    for f in FIELDS:
        t = data.get(f)
        if not isinstance(t, dict) or not t.get("label") or not isinstance(t.get("values"), dict) or not t["values"]:
            raise ValueError(f"vocabulary.toml: [{f}] needs a label and values")
        for v, d in t["values"].items():
            if not isinstance(d, dict) or not d.get("label") or not d.get("definition"):
                raise ValueError(f"vocabulary.toml: {f}.values.{v} needs a label and a definition")
    return data


def values(field):
    """The values of a field that may be used (not withdrawn)."""
    return {v for v, d in load()[field]["values"].items() if not d.get("withdrawn")}
