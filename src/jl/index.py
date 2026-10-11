"""The index service (decision 0018): index exactly the declared input files, query them, stop.

One implementation, with the QLever binaries qlever-index and qlever-server (local.toml [qlever]). Each input
file becomes one named graph (the graph is given with the file). QLever is fed the canonical form of each file
(canonical.py) through a named pipe, so it sees exactly the triples the framework's reader sees (tar members,
RDF-star statements left out).

Indexes live in <cache>/indexes/<key>/, key = hash of the input checksums with their graphs, the QLever version
and the settings; an index is reused while these are the same. Each running server has its own port from the
configured range.

QLever normalises literal values (see rdf.py): query results are good for selecting and joining, but a
generator that copies literals into its output takes them from the files (rdf.read_triples), not from results.
"""

import hashlib
import json
import os
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from . import canonical
from .rdf import BNode, IRI, Literal

SETTINGS = {}   # index settings passed to qlever-index (none so far; recorded in every description)


class IndexServiceError(Exception):
    pass


def qlever_cfg(cfg):
    q = cfg.data.get("qlever", {})
    return {"index": q.get("index", "qlever-index"), "server": q.get("server", "qlever-server"),
            "ports": q.get("ports", [7101, 7199]), "memory": q.get("memory", "4G")}


def qlever_version(cfg):
    exe = qlever_cfg(cfg)["index"]
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=30)
    except OSError as e:
        raise IndexServiceError(f"cannot run {exe}: {e}") from None
    return (out.stdout or out.stderr).strip().splitlines()[0] if (out.stdout or out.stderr) else "unknown"


def free_port(lo, hi):
    for port in range(lo, hi + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise IndexServiceError(f"no free port in {lo}-{hi}")


def _feed(fifo, info, errors):
    try:
        with open(fifo, "w", encoding="utf-8") as f:
            for line in canonical.lines(info):
                f.write(line + "\n")
    except BrokenPipeError:
        pass
    except Exception as e:  # reported by build()
        errors.append(f"{info.get('name')}: {e}")


class Index:
    """An index of declared inputs: build() makes or reuses it, serve() runs a server for queries."""

    def __init__(self, cfg, inputs):
        """inputs: [(path, graph IRI)]; files are named by their checksum."""
        self.cfg, self.q = cfg, qlever_cfg(cfg)
        self.inputs = [(Path(p), g) for p, g in inputs]
        self.version = qlever_version(cfg)
        self.infos = None
        self.dir = None

    def key(self, shas):
        spec = {"inputs": sorted(zip(shas, (g for _, g in self.inputs))), "qlever": self.version,
                "settings": SETTINGS}
        return hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:20]

    def describe(self):
        """For the run record: the service, its version, the settings and the indexed inputs."""
        return {"service": "qlever", "version": self.version, "settings": SETTINGS,
                "inputs": [{"sha256": i["sha256"], "graph": g, "triples": i["triples"]}
                           for i, (_, g) in zip(self.infos or [], self.inputs)]}

    def build(self, log=print):
        self.infos = [canonical.canonical(p, self.cfg) for p, _ in self.inputs]
        base = canonical.cache_dir(self.cfg).parent / "indexes"
        self.dir = base / self.key([i["sha256"] for i in self.infos])
        done = self.dir / "index.json"
        if done.is_file():
            log(f"index {self.dir.name}: reused")
            return self
        if self.dir.exists():
            shutil.rmtree(self.dir)
        self.dir.mkdir(parents=True)
        tmp = Path(tempfile.mkdtemp(prefix="fifo-", dir=self.dir))
        cmd, threads, errors = [self.q["index"], "-i", str(self.dir / "index"), "--no-resource-usage-log"], [], []
        if SETTINGS:
            (self.dir / "settings.json").write_text(json.dumps(SETTINGS), encoding="utf-8")
            cmd += ["-s", str(self.dir / "settings.json")]
        for n, (info, (_, graph)) in enumerate(zip(self.infos, self.inputs)):
            fifo = tmp / f"in{n}.nt"
            os.mkfifo(fifo)
            cmd += ["-f", str(fifo), "-F", "nt", "-g", graph]
            t = threading.Thread(target=_feed, args=(fifo, info, errors), daemon=True)
            t.start()
            threads.append((t, fifo))
        t0 = time.time()
        with open(self.dir / "index-log.txt", "w", encoding="utf-8") as logf:
            rc = subprocess.run(cmd, stdout=logf, stderr=subprocess.STDOUT).returncode
        for t, fifo in threads:   # release writers whose pipe was never opened
            if t.is_alive():
                fd = os.open(fifo, os.O_RDONLY | os.O_NONBLOCK)
                os.close(fd)
                t.join(5)
        shutil.rmtree(tmp, ignore_errors=True)
        if rc != 0 or errors:
            tail = (self.dir / "index-log.txt").read_text(encoding="utf-8", errors="replace").splitlines()[-5:]
            raise IndexServiceError(f"qlever-index failed ({rc}): " + "; ".join(errors + tail))
        desc = self.describe() | {"seconds": round(time.time() - t0, 1)}
        done.write_text(json.dumps(desc, indent=1) + "\n", encoding="utf-8")
        log(f"index {self.dir.name}: {sum(i['triples'] for i in self.infos):,} triples, "
            f"{len(self.infos)} files, {desc['seconds']} s")
        return self

    def serve(self):
        return Server(self)


class Server:
    """A running qlever-server on an index; use as a context manager."""

    def __init__(self, index):
        self.index, self.proc, self.port = index, None, None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.stop()

    def start(self, timeout=120):
        lo, hi = self.index.q["ports"]
        self.port = free_port(lo, hi)
        self.logf = open(self.index.dir / f"server-{self.port}.log", "w", encoding="utf-8")
        self.proc = subprocess.Popen(
            [self.index.q["server"], "-i", str(self.index.dir / "index"), "-p", str(self.port),
             "-m", self.index.q["memory"], "--no-metrics-log", "--no-resource-usage-log"],
            stdout=self.logf, stderr=subprocess.STDOUT)
        t0 = time.time()
        while time.time() - t0 < timeout:
            if self.proc.poll() is not None:
                raise IndexServiceError(f"qlever-server stopped (see {self.logf.name})")
            try:
                self.ask("ASK { }")
                return self
            except (urllib.error.URLError, ConnectionError, OSError):
                time.sleep(0.2)
        self.stop()
        raise IndexServiceError("qlever-server did not answer in time")

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.proc = None
        if getattr(self, "logf", None):
            self.logf.close()

    @property
    def url(self):
        return f"http://127.0.0.1:{self.port}"

    def request(self, query, accept):
        data = urllib.parse.urlencode({"query": query}).encode()
        req = urllib.request.Request(self.url, data=data, headers={
            "Accept": accept, "Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=3600) as r:
            return r.read()

    def ask(self, query):
        return json.loads(self.request(query, "application/sparql-results+json")).get("boolean")

    def select(self, query):
        """Rows of a SELECT as dicts of terms (IRI, Literal, BNode); unbound variables are left out."""
        res = json.loads(self.request(query, "application/sparql-results+json"))
        return [{k: term(v) for k, v in row.items()} for row in res["results"]["bindings"]]


def term(v):
    t = v.get("type")
    if t == "uri":
        return IRI(v["value"])
    if t == "bnode":
        return BNode(v["value"])
    return Literal(v["value"], IRI(v["datatype"]) if v.get("datatype") else None, v.get("xml:lang"))
