"""Tests of the RDF reader, the Turtle writer and the canonical form: python3 -m unittest (repository root)."""

import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jl import canonical, graph, rdf, turtle  # noqa: E402
from jl.rdf import IRI, BNode, Literal, XSD  # noqa: E402

EX = "http://example.org/"


def ttl(text):
    return list(rdf.TurtleParser(io.StringIO(text), "test").triples())


class TurtleReader(unittest.TestCase):
    def test_terms(self):
        t = ttl('''@prefix ex: <http://example.org/> .
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        ex:s a ex:C ; ex:p "x"@de-DE , 'y' , """multi
line "q" """ , 42 , -1.5 , 1e3 , true , "042"^^xsd:integer ; ex:q ex:o.
        ex:a\\.b ex:p ex:c%20d .''')
        objs = [o for _, _, o in t]
        self.assertEqual(t[0], (IRI(EX + "s"), IRI(rdf.RDF_TYPE), IRI(EX + "C")))
        self.assertIn(Literal("x", None, "de-DE"), objs)
        self.assertIn(Literal("y"), objs)
        self.assertIn(Literal('multi\nline "q" '), objs)
        self.assertIn(Literal("42", XSD + "integer"), objs)
        self.assertIn(Literal("-1.5", XSD + "decimal"), objs)
        self.assertIn(Literal("1e3", XSD + "double"), objs)
        self.assertIn(Literal("true", XSD + "boolean"), objs)
        self.assertIn(Literal("042", XSD + "integer"), objs)     # the lexical form is kept
        self.assertIn((IRI(EX + "s"), IRI(EX + "q"), IRI(EX + "o")), t)   # statement ends with "."
        self.assertIn((IRI(EX + "a.b"), IRI(EX + "p"), IRI(EX + "c%20d")), t)

    def test_base_escapes_and_trailing_semicolons(self):
        t = ttl('@base <http://example.org/> . <s> <p> "a\\tb\\u00e4\\U0001F600" ;; <q> <r> ; .')
        self.assertEqual(t[0][2], Literal("a\tbä\U0001F600"))
        self.assertEqual(t[1], (IRI(EX + "s"), IRI(EX + "q"), IRI(EX + "r")))

    def test_blank_nodes_and_lists(self):
        t = ttl('@prefix ex: <http://example.org/> . ex:s ex:p [ ex:q 1 ] , _:x ; ex:l ( 1 2 ) .')
        self.assertTrue(any(isinstance(o, BNode) for _, _, o in t))
        self.assertIn((IRI(EX + "s"), IRI(EX + "p"), BNode("x")), t)
        self.assertEqual(sum(1 for _, p, _ in t if p == rdf.RDF + "first"), 2)

    def test_rdf_star_left_out(self):
        report = {}
        t = list(rdf.TurtleParser(io.StringIO(
            '<< <http://e/s> <http://e/p> <http://e/o> >> <http://e/q> "x" .\n<http://e/a> <http://e/b> <http://e/c> .'),
            "test", report).triples())
        self.assertEqual(len(t), 1)
        self.assertEqual(report["rdf_star"], 1)

    def test_errors(self):
        for bad in ('ex:s ex:p ex:o .', '<http://e/s> <http://e/p> "x" ', '<http://e/s> <http://e/p> "x\\q" .'):
            with self.assertRaises(rdf.ParseError):
                ttl(bad)

    def test_long_literal_across_chunks(self):
        big = "x" * (3 * rdf.TurtleParser.CHUNK)
        t = ttl(f'<http://e/s> <http://e/p> """{big}""" . <http://e/s> <http://e/p> "y" .')
        self.assertEqual(t[0][2].value, big)
        self.assertEqual(len(t), 2)

    def test_small_chunks(self):
        doc = ('@prefix ex: <http://example.org/> .\n# comment\nex:s ex:p 1.5 , "abc"@en , """long\nvalue""" ;\n'
               '    ex:q ex:o , <http://example.org/x> . ex:t ex:p -12 .\n')
        old = rdf.TurtleParser.CHUNK
        rdf.TurtleParser.CHUNK = 3
        try:
            small = ttl(doc)
        finally:
            rdf.TurtleParser.CHUNK = old
        self.assertEqual(small, ttl(doc))
        self.assertIn(Literal("1.5", XSD + "decimal"), [o for _, _, o in small])


class NTriplesReader(unittest.TestCase):
    def test_lines(self):
        t = list(rdf.parse_ntriples(io.StringIO(
            '# comment\n<http://e/s> <http://e/p> "a\\"b"@en .\n\n_:b1 <http://e/p> "1"^^<http://e/dt> . # c\n')))
        self.assertEqual(t[0][2], Literal('a"b', None, "en"))
        self.assertEqual(t[1], (BNode("b1"), IRI("http://e/p"), Literal("1", "http://e/dt")))
        with self.assertRaises(rdf.ParseError):
            list(rdf.parse_ntriples(io.StringIO("<http://e/s> <http://e/p> .\n")))


class Writer(unittest.TestCase):
    triples = [
        (IRI(EX + "s"), IRI("http://xmlns.com/foaf/0.1/name"), Literal("Ä \"q\"\n", None, "de")),
        (IRI(EX + "s"), IRI(rdf.RDF_TYPE), IRI("http://xmlns.com/foaf/0.1/Person")),
        (IRI(EX + "s"), IRI("http://data.judaicalink.org/ontology/x"), Literal("1750", XSD + "integer")),
        (IRI(EX + "s"), IRI("http://data.judaicalink.org/ontology/x"), IRI("http://data.judaicalink.org/ontology/Amarillo,Tex.")),
        (IRI(EX + "s"), IRI("http://data.judaicalink.org/ontology/x"), IRI("http://www.wikidata.org/entity/Q1%20x")),
        (IRI(EX + "s"), IRI("http://data.judaicalink.org/ontology/x"), IRI("http://data.judaicalink.org/ontology/Göppingen")),
    ]

    def test_round_trip_and_determinism(self):
        with tempfile.TemporaryDirectory() as d:
            a = turtle.write(Path(d) / "a.ttl.gz", self.triples, header=["test"])
            b = turtle.write(Path(d) / "b.ttl.gz", list(reversed(self.triples)) * 2, header=["test"])
            self.assertEqual(a["sha256"], b["sha256"])
            self.assertEqual(a["triples"], len(self.triples))
            back = list(rdf.read_triples(Path(d) / "a.ttl.gz"))
            self.assertEqual(sorted(map(rdf.nt_line, *zip(*back))), sorted(map(rdf.nt_line, *zip(*self.triples))))

    def test_layout(self):
        text, _ = turtle.turtle_text(self.triples)
        lines = text.splitlines()
        self.assertTrue(lines[0].startswith("@prefix foaf:"))
        self.assertIn("    a foaf:Person ;", lines)
        self.assertIn("<http://data.judaicalink.org/ontology/Amarillo,Tex.>", text)   # not a safe local name
        self.assertIn("wd:Q1%20x", text)
        self.assertIn("jl:Göppingen", text)
        self.assertIn('"1750"^^xsd:integer', text)

    def test_no_blank_nodes(self):
        with self.assertRaises(ValueError):
            turtle.turtle_text([(BNode("b"), IRI(EX + "p"), IRI(EX + "o"))])


class Canonical(unittest.TestCase):
    def test_normalisation(self):
        self.assertEqual(rdf.nt(Literal("x", XSD + "string"), canonical=True), '"x"')
        self.assertEqual(rdf.nt(Literal("x", None, "DE"), canonical=True), '"x"@de')
        self.assertEqual(rdf.nt(Literal("a\u0001\\")), '"a\\u0001\\\\"')

    def test_compare(self):
        r = canonical.compare(["a", "b", "d"], ["b", "c", "d"])
        self.assertEqual((r["common"], r["only_a"], r["only_b"], r["identical"]), (2, 1, 1, False))

    def test_sorted_unique_in_chunks(self):
        old = canonical.CHUNK_LINES
        canonical.CHUNK_LINES = 3
        try:
            with tempfile.TemporaryDirectory() as d:
                out = list(canonical._sorted_unique(iter(["d", "a", "c", "a", "b", "d", "e"]), d))
        finally:
            canonical.CHUNK_LINES = old
        self.assertEqual(out, ["a", "b", "c", "d", "e"])


class Index(unittest.TestCase):
    def test_patterns(self):
        g = graph.Graph()
        s, t, p, q = (IRI(EX + x) for x in ("s", "t", "p", "q"))
        for tr in [(s, p, Literal("b")), (s, p, Literal("a")), (t, p, Literal("a")), (s, q, t), (s, p, Literal("b"))]:
            g.add(*tr)
        self.assertEqual(len(g), 4)
        self.assertEqual(g.objects(s, p), [Literal("b"), Literal("a")])      # file order
        self.assertEqual(g.subjects(p, Literal("a")), [s, t])
        self.assertEqual(g.value(s, q), t)
        self.assertIsNone(g.value(t, q))
        with self.assertRaises(ValueError):
            g.value(s, p)
        self.assertEqual(len(list(g.triples(None, p, None))), 3)
        self.assertEqual(list(g.triples(None, None, t)), [(s, q, t)])
        self.assertIn((t, p, Literal("a")), g)
        g.add(t, q, s)
        self.assertEqual(g.subjects(q, s), [t])                              # index kept up to date


class InvalidIRI(unittest.TestCase):
    def test_writer_refuses(self):
        from jl import turtle
        from jl.rdf import IRI, Literal
        with self.assertRaises(ValueError):
            turtle.turtle_text([(IRI("http://a/x|y"), IRI("http://a/p"), Literal("v"))])
        turtle.turtle_text([(IRI("http://a/x%7Cy"), IRI("http://a/p"), Literal("v"))])


if __name__ == "__main__":
    unittest.main()


class Surrogates(unittest.TestCase):
    def test_pairs(self):
        from jl.rdf import unescape_string
        self.assertEqual(unescape_string(r"a😀b"), "a\U0001F600b")   # a pair: its character
        self.assertEqual(unescape_string(r"x\uD83Dy"), "x�y")             # alone: the replacement character
        self.assertEqual(unescape_string(r"é"), "é")
