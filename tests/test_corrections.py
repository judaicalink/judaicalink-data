"""Correction datasets (decision 0023): the fixed form of the deletions file; inputs read without deleted triples."""

import gzip
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jl import corrections, generator  # noqa: E402
from jl.rdf import IRI, XSD, Literal  # noqa: E402

S = IRI("http://data.judaicalink.org/data/x/a")
P = IRI("http://www.w3.org/2002/07/owl#sameAs")
O = IRI("http://example.org/page")
L = (S, IRI("http://data.judaicalink.org/ontology/birthDate"), Literal('1 "x" #2', None, "de"))


class Form(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "c-deletions.ru.gz"
            info = corrections.write(path, [(["why"], [(S, P, O)]), (["a literal"], [L])])
            self.assertEqual(info["deletions"], 2)
            text = gzip.decompress(path.read_bytes()).decode()
            self.assertIn("DELETE { GRAPH ?g { ?s ?p ?o } }", text)
            self.assertIn("# why", text)
            self.assertEqual({corrections.key(t) for t in corrections.read(path)},
                             {corrections.key((S, P, O)), corrections.key(L)})
            self.assertEqual(path.read_bytes(), (corrections.write(path, [(["why"], [(S, P, O)]), (["a literal"], [L])])
                                                 and path.read_bytes()))   # deterministic

    def test_key(self):
        self.assertEqual(corrections.key((S, P, Literal("x", XSD + "string"))), corrections.key((S, P, Literal("x"))))
        self.assertEqual(corrections.key((S, P, Literal("x", None, "DE"))), corrections.key((S, P, Literal("x", None, "de"))))

    def test_other_forms_rejected(self):
        for bad in ["DELETE WHERE { GRAPH ?g { <a:b> <a:c> <a:d> } }",
                    "DELETE { GRAPH ?g { ?s ?p ?o } } WHERE { VALUES (?s ?p ?o) { (_:b <a:c> <a:d>) } GRAPH ?g { ?s ?p ?o } }",
                    "DELETE { GRAPH ?g { ?s ?p ?o } } WHERE { VALUES (?s ?p ?o) { (<a:b> <a:c> <a:d>) } GRAPH ?g { ?s ?p ?o } } "
                    "INSERT DATA { <a:b> <a:c> <a:d> }"]:
            with self.assertRaises(corrections.ParseError):
                list(corrections.DeletionsParser(io.StringIO(bad), "x").rows())


class Inputs(unittest.TestCase):
    def test_deleted_triples_left_out(self):
        with tempfile.TemporaryDirectory() as d:
            data = Path(d) / "data.nt"
            data.write_text(f"<{S}> <{P}> <{O}> .\n<{S}> <{P}> <http://example.org/other> .\n")
            run = generator.Run("t", "run-x", Path(d), {}, {"data": [{"path": data}]}, io.StringIO(),
                                frozenset({corrections.key((S, P, O))}))
            self.assertEqual([t[2] for t in run.triples("data")], ["http://example.org/other"])
            self.assertEqual(len(run.graph("data")), 1)
            self.assertEqual(run.deleted_from, {"data": 2})


if __name__ == "__main__":
    unittest.main()
