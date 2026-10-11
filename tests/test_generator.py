"""Tests of running generators (jl.generator): python3 -m unittest discover -s tests."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jl import config, generator, rdf  # noqa: E402

GENERATE = '''
from jl.rdf import IRI, Literal
INPUTS = {"data": "inputs:test/data-2020/data.txt"}
PARAMS = {"times": 1, "label": "x"}

def generate(run):
    text = run.input("data").read_text()
    run.note("a note")
    t = [(IRI("http://example.org/s%d" % i), IRI("http://example.org/p"), Literal(text + run.params["label"]))
         for i in range(run.params["times"])]
    run.write_turtle("test.ttl.gz", t)
'''


class FakeEntry:
    def version(self, vid):
        return None


class FakeCatalog:
    def get(self, slug):
        return FakeEntry() if slug == "test" else None


class Generate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        from jl import inputs
        (t / "src").mkdir()
        (t / "src" / "data.txt").write_text("hello ")
        inputs.add(t / "inputs", "test/data-2020", [t / "src" / "data.txt"],
                   {"title": "Test data", "origin": "https://example.org/data.txt", "description": "a test file"})
        (t / "generators" / "test").mkdir(parents=True)
        (t / "generators" / "test" / "generate.py").write_text(GENERATE)
        self.cfg = config.Config({"build": str(t / "build"), "inputs": str(t / "inputs")}, None)
        self.patches = [mock.patch.object(generator, "GENERATORS", t / "generators"),
                        mock.patch.object(generator.catalog, "Catalog", FakeCatalog)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def test_run(self):
        d, rec = generator.generate(self.cfg, "test", ["times=3"], log=lambda *a: None)
        self.assertEqual(rec["status"], "ok", rec.get("error"))
        self.assertTrue(d.name.startswith("run-"))
        self.assertEqual(rec["params"], {"times": 3, "label": "x"})
        self.assertEqual(rec["inputs"][0]["ref"], "inputs:test/data-2020/data.txt")
        self.assertEqual(rec["input_descriptions"]["inputs:test/data-2020"]["origin"], "https://example.org/data.txt")
        self.assertNotIn("path", rec["inputs"][0])                      # no local paths in the record
        self.assertNotIn(self.tmp.name, json.dumps(rec))
        self.assertEqual(rec["notes"], ["a note"])
        self.assertEqual([(f["path"], f["triples"]) for f in rec["files"]], [("test.ttl.gz", 3)])
        triples = list(rdf.read_triples(d / "test.ttl.gz"))
        self.assertEqual(triples[0][2], rdf.Literal("hello x"))
        self.assertEqual(json.loads((d / "run.json").read_text())["run"], d.name)

    def test_inputs_check(self):
        from jl import inputs
        root = self.cfg.path("inputs")
        self.assertEqual(inputs.check(root), [("test/data-2020", 1, [])])
        (root / "test" / "data-2020" / "extra.txt").write_text("x")
        (root / "test" / "data-2020" / "data.txt").write_text("hello!")
        problems = inputs.check(root)[0][2]
        self.assertEqual(problems, ["data.txt: checksum differs", "extra.txt: not described in input.toml"])
        _, rec = generator.generate(self.cfg, "test", [], log=lambda *a: None)
        self.assertEqual(rec["status"], "failed")
        self.assertIn("differs from input.toml", rec["error"])

    def test_failures(self):
        with self.assertRaises(generator.GeneratorError):
            generator.generate(self.cfg, "test", ["nope=1"])
        with self.assertRaises(generator.GeneratorError):
            generator.generate(self.cfg, "missing")
        d, rec = generator.generate(self.cfg, "test", [], ["data=test/2020-01-01/x"])
        self.assertEqual(rec["status"], "failed")
        self.assertIn("no such version", rec["error"])
        self.assertTrue((d / "run.json").is_file())


if __name__ == "__main__":
    unittest.main()
