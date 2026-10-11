# judaicalink-agents: generator

The persons and software agents named in the `-meta` files (decision 0018), generated from the registry
[`catalog/agents.toml`](../../catalog/agents.toml).

## Framework generator

`generate.py` (2026-10-11): reads the registry (input `repo:catalog/agents.toml`, a file of this repository fixed
by the commit like the code) and writes `judaicalink-agents.ttl.gz`: each person `datasets/agents/persons/<n>`
with `foaf:name` and optional `rdfs:seeAlso` links (a withdrawn person keeps only the IRI and its type), each
software agent `datasets/agents/software/<name>` with label and homepage. This dataset is the only place where
the names of persons are published as data; the `-meta` files name agents by IRI.
