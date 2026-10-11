"""The agents registry catalog/agents.toml (decision 0018).

Persons are numbered in sequence (never reused) and named only in the dataset judaicalink-agents; everything
else (the -meta files) names them by IRI. Software agents keep descriptive names.
"""

import tomllib

from .config import CATALOG

REGISTRY = CATALOG / "agents.toml"
BASE = "http://data.judaicalink.org/datasets/agents/"


class AgentError(LookupError):
    pass


def person_iri(n):
    return f"{BASE}persons/{n}"


def software_iri(name):
    return f"{BASE}software/{name}"


class Registry:
    def __init__(self, path=None):
        path = path or REGISTRY
        self.path = path
        self.persons = {}    # number -> table
        self.software = {}   # name -> table
        self.errors = []
        if not path.is_file():
            self.errors.append(f"{path.name} does not exist")
            return
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as e:
            self.errors.append(f"{path.name}: {e}")
            return
        for key, t in (data.get("persons") or {}).items():
            if not key.isdigit() or int(key) < 1 or str(int(key)) != key:
                self.errors.append(f"persons.{key}: the key must be a number (1, 2, …)")
            elif not isinstance(t, dict) or bool(t.get("name")) == bool(t.get("withdrawn")):
                self.errors.append(f"persons.{key}: give either name or withdrawn")
            else:
                self.persons[int(key)] = t
        for key, t in (data.get("software") or {}).items():
            if not isinstance(t, dict) or not t.get("label"):
                self.errors.append(f"software.{key}: label is required")
            else:
                self.software[key] = t
        for k in set(data) - {"persons", "software"}:
            self.errors.append(f"unknown table '{k}'")
        names = [t["name"] for t in self.persons.values() if t.get("name")]
        for n in sorted({n for n in names if names.count(n) > 1}):
            self.errors.append(f"the name '{n}' is registered twice")

    def number(self, name):
        """The number of a person by name; AgentError if the name is not registered."""
        for n, t in self.persons.items():
            if t.get("name") == name:
                return n
        raise AgentError(f"'{name}' is not in {self.path.name} (decision 0018: add the person with the next number)")

    def person(self, name):
        return person_iri(self.number(name))

    def software_agent(self, name):
        if name not in self.software:
            raise AgentError(f"software agent '{name}' is not in {self.path.name}")
        return software_iri(name)
