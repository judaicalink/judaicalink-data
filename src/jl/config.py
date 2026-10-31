"""Paths of the repository and the local configuration (local.toml, not committed).

local.toml names where the data is on this machine; the template is local.example.toml. Paths in it are
relative to the repository root. Nothing in it is ever written into a catalogue entry, run record or -meta
file (decision 0018: no local paths in what is published).
"""

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "catalog"
DECISIONS = ROOT / "docs" / "decisions"
GENERATORS = ROOT / "generators"
LOCAL = ROOT / "local.toml"


class ConfigError(Exception):
    pass


class Config:
    def __init__(self, data, source):
        self.data = data
        self.source = source   # the file read, or None

    def path(self, key):
        """A configured directory as an absolute path, or None if it is not configured."""
        value = self.data.get(key)
        return (ROOT / value).resolve() if isinstance(value, str) else None

    def paths(self, key):
        value = self.data.get(key, [])
        return [(ROOT / v).resolve() for v in value] if isinstance(value, list) else []

    def require(self, key):
        """A configured directory; raises ConfigError with a hint if it is missing."""
        p = self.path(key)
        if p is None:
            where = self.source.name if self.source else "local.toml (copy local.example.toml)"
            raise ConfigError(f"'{key}' is not configured in {where}")
        return p

    @property
    def store(self):
        return self.path("store")

    @property
    def pruned(self):
        """Where the files of pruned versions are kept (decision 0041): not public, layout of the store."""
        return self.path("pruned")

    def version_dir(self, slug, version):
        """The directory of a version's files: the store, or for a pruned version the pruned area."""
        return self.require("pruned" if version.get("pruned") else "store") / slug / version["version"]

    @property
    def build(self):
        return self.path("build")


def load(path=LOCAL):
    if not path.exists():
        return Config({}, None)
    try:
        return Config(tomllib.loads(path.read_text(encoding="utf-8")), path)
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"{path.name}: {e}") from None
