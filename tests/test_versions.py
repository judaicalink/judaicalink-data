"""Tests of add-version and render-meta (jl.versions) on a temporary catalogue, store and build area:
python3 -m unittest discover -s tests."""

import gzip
import json
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jl import agents, catalog, config, generator, meta, rdf, runs, versions  # noqa: E402

GENERATE = '''
from jl.rdf import IRI, Literal
INPUTS = {"data": "src/2020-01-01/data.txt"}
PARAMS = {"n": 2}

def generate(run):
    text = run.input("data").read_text().strip()
    t = [(IRI("http://data.judaicalink.org/data/test/%d" % i), IRI("http://www.w3.org/2004/02/skos/core#prefLabel"),
          Literal(text)) for i in range(run.params["n"])]
    run.write_turtle("test.ttl.gz", t)
    run.copy_input("data")
'''

ENTRY = '''+++
slug = "test"
title = "A test"
author = "Ann Example"
namespaces = ["test"]
kind = "complement"
method = ["deterministic", "rule-based"]

# a comment that must stay

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"

[files]
"data.txt" = "The input."

[[changelog]]
date = "2020-01-01"
author = "Ann Example"
text = "Started."
+++

The test dataset.

<!--more-->

More.
'''

SRC = '''+++
slug = "src"
title = "Source"
author = "Ann Example"

[license]
name = "CC0"

[[versions]]
version = "2020-01-01"

  [[versions.files]]
  path = "data.txt"
+++
'''

REGISTRY = '''
[persons.1]
name = "Ann Example"

[software.judaicalink-data]
label = "the framework"
'''

CLEAN = ("a" * 40, [])


class Versions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = self.t = Path(self.tmp.name).resolve()
        (t / "catalog").mkdir()
        (t / "catalog" / "test.md").write_text(ENTRY)
        (t / "catalog" / "src.md").write_text(SRC)
        (t / "catalog" / "agents.toml").write_text(REGISTRY)
        (t / "store" / "src" / "2020-01-01").mkdir(parents=True)
        (t / "store" / "src" / "2020-01-01" / "data.txt").write_text("hello\n")
        (t / "generators" / "test").mkdir(parents=True)
        (t / "generators" / "test" / "generate.py").write_text(GENERATE)
        self.cfg = config.Config({"build": str(t / "build"), "store": str(t / "store")}, None)
        gens = t / "generators"
        self.patches = [mock.patch.object(catalog, "CATALOG", t / "catalog"),
                        mock.patch.object(agents, "REGISTRY", t / "catalog" / "agents.toml"),
                        mock.patch.object(generator, "GENERATORS", gens),
                        mock.patch.object(runs, "GENERATORS", gens),
                        mock.patch.object(catalog, "GENERATORS", gens),
                        mock.patch.object(generator, "code_state", lambda slug, files=(): CLEAN),
                        mock.patch.object(versions, "framework_state", lambda: CLEAN),
                        mock.patch.object(versions, "git_user", lambda: "Ann Example")]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def run_generator(self):
        d, rec = generator.generate(self.cfg, "test", [], log=lambda *a: None)
        self.assertEqual(rec["status"], "ok", rec.get("error"))
        return d, rec

    def test_add_version(self):
        d, rec = self.run_generator()
        vid, target, v, warnings = versions.add_version(self.cfg, "test", rec["run"])
        self.assertEqual(vid, rec["started"][:10])
        self.assertEqual(target, self.t / "store" / "test" / vid)
        # header comments; the triples are those of the run
        text = gzip.decompress((target / "test.ttl.gz").read_bytes()).decode()
        self.assertTrue(text.startswith(f"# JudaicaLink dataset test, version {vid}\n"
                                        f"# http://data.judaicalink.org/datasets/test/{vid}\n\n"))
        self.assertEqual(len(list(rdf.read_triples(target / "test.ttl.gz"))), 2)
        # catalogue: version (newest first), changelog, comment kept
        entry_text = (self.t / "catalog" / "test.md").read_text()
        self.assertIn("# a comment that must stay", entry_text)
        e = catalog.read_entry(self.t / "catalog" / "test.md")
        self.assertEqual([x["version"] for x in e.versions()], [vid])
        files = {f["path"]: f for f in e.version(vid)["files"]}
        self.assertEqual(set(files), {"test.ttl.gz", "data.txt", "test-meta.ttl.gz"})
        self.assertEqual(files["test.ttl.gz"]["sha256"], catalog.sha256(target / "test.ttl.gz"))
        self.assertEqual(files["test.ttl.gz"]["triples"], 2)
        self.assertEqual(e.changelog()[0]["version"], vid)
        self.assertEqual(e.version(vid)["commit"], "a" * 40)
        self.assertIsNone(e.stable)
        # run record of the version: files as in the version, the run keeps record and log only
        record = json.loads(runs.record_path("test", vid).read_text())
        self.assertEqual(record["version"], vid)
        self.assertEqual({f["path"] for f in record["files"]}, {"test.ttl.gz", "data.txt"})
        self.assertEqual(sorted(p.name for p in d.iterdir()), ["log.txt", "run.json"])
        self.assertEqual(runs.version_of_run("test", rec["run"]), vid)
        # the -meta: graph content, persons by IRI only, input version named
        m = {(str(s), str(p), o if isinstance(o, rdf.Literal) else str(o))
             for s, p, o in rdf.read_triples(target / "test-meta.ttl.gz")}
        V = f"http://data.judaicalink.org/datasets/test/{vid}"
        self.assertIn((V, "http://purl.org/dc/terms/creator", agents.person_iri(1)), m)
        self.assertIn((V, "http://www.w3.org/ns/prov#wasDerivedFrom",
                       "http://data.judaicalink.org/datasets/src/2020-01-01"), m)
        self.assertIn((V, "http://rdfs.org/ns/void#triples", rdf.Literal("2", rdf.XSD + "integer")), m)
        self.assertFalse(any("Ann Example" in str(o) for _, _, o in m))
        D, DCT = "http://data.judaicalink.org/datasets/test", "http://purl.org/dc/terms/"
        self.assertIn((D, DCT + "type", "http://data.judaicalink.org/datasets/vocabulary/kind/complement"), m)
        self.assertIn((D, DCT + "type", "http://data.judaicalink.org/datasets/vocabulary/method/rule-based"), m)
        self.assertIn((D, DCT + "type", "http://data.judaicalink.org/datasets/vocabulary/method/automated"), m)
        self.assertIn((D, DCT + "abstract", rdf.Literal("The test dataset.")), m)
        self.assertIn((D, DCT + "description", rdf.Literal("The test dataset.\n\nMore.")), m)
        # the store holds exactly the catalogued files
        out = []
        n, errors, _ = catalog.check(catalog=self.t / "catalog", dumps=[self.t / "store"], complete=True,
                                     out=out.append, registry=agents.Registry())
        self.assertEqual(errors, 0, out)
        # nothing to do for render-meta; a changed title rewrites it and updates the entry
        self.assertEqual(versions.render_meta(self.cfg, "test", vid)[0], "unchanged")
        p = self.t / "catalog" / "test.md"
        p.write_text(p.read_text().replace('title = "A test"', 'title = "A better test"'))
        status, info = versions.render_meta(self.cfg, "test", vid)
        self.assertEqual(status, "written")
        e = catalog.read_entry(p)
        meta_file = next(f for f in e.version(vid)["files"] if f["path"] == "test-meta.ttl.gz")
        self.assertEqual(meta_file["sha256"], catalog.sha256(target / "test-meta.ttl.gz"))
        self.assertEqual(versions.render_meta(self.cfg, "test", vid)[0], "unchanged")
        # an unpublished development version (latest, not stable) can be removed again, confirmed
        with self.assertRaises(versions.VersionError):
            versions.remove_version(self.cfg, "test", vid, warn=lambda m: None)
        versions.remove_version(self.cfg, "test", vid, latest_ok=True, warn=lambda m: None)
        e = catalog.read_entry(self.t / "catalog" / "test.md")
        self.assertEqual(e.versions(), [])
        self.assertIn("# a comment that must stay", (self.t / "catalog" / "test.md").read_text())
        self.assertFalse(target.exists() or runs.record_path("test", vid).exists())
        # a second run of the same day gets -2
        _, rec2 = self.run_generator()
        vid2 = versions.add_version(self.cfg, "test", rec2["run"])[0]
        _, rec3 = self.run_generator()
        self.assertEqual(versions.add_version(self.cfg, "test", rec3["run"], dry_run=True)[0], vid2 + "-2")

    def test_refusals(self):
        _, rec = self.run_generator()
        run = rec["run"]
        with self.assertRaises(versions.VersionError):
            versions.add_version(self.cfg, "test", run, version="meta")
        with self.assertRaises(agents.AgentError):
            versions.add_version(self.cfg, "test", run, author="Nobody")
        path = self.cfg.build / "test" / run / "run.json"
        rec["uncommitted"] = ["generators/test/generate.py"]
        path.write_text(json.dumps(rec))
        with self.assertRaisesRegex(versions.VersionError, "uncommitted"):
            versions.add_version(self.cfg, "test", run)
        rec["uncommitted"] = []
        rec["inputs"][0]["ref"] = "src/run-20200101T000000Z/data.txt"
        path.write_text(json.dumps(rec))
        with self.assertRaisesRegex(versions.VersionError, "is a run"):
            versions.add_version(self.cfg, "test", run)
        # a dry run changes nothing
        rec["inputs"][0]["ref"] = "src/2020-01-01/data.txt"
        path.write_text(json.dumps(rec))
        before = (self.t / "catalog" / "test.md").read_text()
        vid, target, _, _ = versions.add_version(self.cfg, "test", run, dry_run=True)
        self.assertEqual((self.t / "catalog" / "test.md").read_text(), before)
        self.assertFalse((self.t / "store" / "test").exists())
        self.assertTrue((target / "catalog-entry.md").is_file())

    def test_import(self):
        # files made elsewhere: a run, kept byte for byte, then a version with its own issued date
        f = self.t / "sent.ttl"
        f.write_text('<http://data.judaicalink.org/data/test/x> <http://www.w3.org/2000/01/rdf-schema#label> "x" .\n')
        with self.assertRaises(versions.VersionError):
            versions.import_files(self.cfg, "test", [f], None, "no origin")
        d, rec = versions.import_files(self.cfg, "test", [f], "sent by mail, 2026-10-01", "one label")
        self.assertEqual(rec["mode"], "import")
        vid, target, v, warnings = versions.add_version(self.cfg, "test", rec["run"], issued="2026-09-30")
        self.assertEqual(v["issued"], "2026-09-30")
        self.assertEqual((target / "sent.ttl").read_bytes(), f.read_bytes())    # no header
        self.assertEqual(v["files"][0]["triples"], 1)
        b = self.t / "blank.ttl"
        b.write_text('_:b <http://www.w3.org/2000/01/rdf-schema#label> "x" .\n')
        with self.assertRaisesRegex(versions.VersionError, "blank nodes"):
            versions.import_files(self.cfg, "test", [b], "o", "d")
        # a record attached to a catalogued version made outside the framework; nothing of it changes
        before = catalog.sha256(self.t / "store" / "src" / "2020-01-01" / "data.txt")
        rec = versions.import_version(self.cfg, "src", "2020-01-01", "Made by hand.",
                                      sources=["https://example.org/code.py"], notes=["checked"])
        self.assertEqual(json.loads(runs.record_path("src", "2020-01-01").read_text())["files"][0]["sha256"], before)
        with self.assertRaises(versions.VersionError):
            versions.import_version(self.cfg, "src", "2020-01-01", "again")
        status, _ = versions.render_meta(self.cfg, "src", "2020-01-01")
        self.assertEqual(status, "written")
        m = list(rdf.read_triples(self.t / "store" / "src" / "2020-01-01" / "src-meta.ttl.gz"))
        objs = {o for _, _, o in m}
        self.assertIn(rdf.Literal("Made by hand."), objs)
        self.assertIn("https://example.org/code.py", objs)
        e = catalog.read_entry(self.t / "catalog" / "src.md")
        self.assertEqual([x["path"] for x in e.version("2020-01-01")["files"]], ["data.txt", "src-meta.ttl.gz"])

    def test_set_file_text(self):
        text = SRC
        data = tomllib.loads(versions.split_entry(text)[1])
        new = versions.set_file_text(text, data, "2020-01-01", {"path": "data.txt", "bytes": 6})
        self.assertIn('  path = "data.txt"\n  bytes = 6', new)
        new = versions.set_file_text(new, tomllib.loads(versions.split_entry(new)[1]), "2020-01-01",
                                     {"path": "src-meta.ttl.gz", "bytes": 10, "sha256": "0" * 64})
        files = tomllib.loads(versions.split_entry(new)[1])["versions"][0]["files"]
        self.assertEqual([f["path"] for f in files], ["data.txt", "src-meta.ttl.gz"])

    def test_meta_statistics(self):
        p = self.t / "x.nt"
        p.write_text('<http://a/1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://a/C> .\n'
                     '<http://a/1> <http://a/p> "x" .\n<http://a/2> <http://a/p> "y" .\n'
                     '<http://a/3> <http://purl.org/dc/terms/isReplacedBy> <http://a/1> .\n')
        from jl import canonical
        cfg = config.Config({"cache": str(self.t / "cache")}, None)
        s = meta.statistics([canonical.canonical(p, cfg)])
        self.assertEqual(s, {"triples": 4, "distinct_subjects": 3, "current_subjects": 2, "properties": 3,
                             "classes": 1})


if __name__ == "__main__":
    unittest.main()


class RemoveGuards(unittest.TestCase):
    """remove-version refuses stable versions, asks for --latest on the latest one, and never touches anything
    when it refuses (decision 0018)."""

    def entry(self, stable):
        from jl import catalog
        data = {"slug": "x", "stable": stable, "versions": [{"version": "2020-01-01", "issued": "2020-01-01"},
                                                            {"version": "2026-01-01", "issued": "2026-01-01"}]}
        return catalog.Entry(Path("x.md"), data, "")

    def run_remove(self, stable, vid, latest_ok=False):
        from unittest import mock
        from jl import versions
        fake = mock.Mock()
        fake.get.return_value = self.entry(stable)
        fake.entries = {}
        with mock.patch.object(versions.catalog, "Catalog", return_value=fake), \
                mock.patch.object(versions.runs, "version_record", return_value={}):
            return versions.remove_version(None, "x", vid, latest_ok=latest_ok, warn=lambda m: None)

    def test_stable_refused(self):
        from jl.versions import VersionError
        with self.assertRaisesRegex(VersionError, "stable version"):
            self.run_remove("2020-01-01", "2020-01-01")

    def test_latest_needs_confirmation(self):
        from jl.versions import VersionError
        with self.assertRaisesRegex(VersionError, "latest version"):
            self.run_remove("2020-01-01", "2026-01-01")
