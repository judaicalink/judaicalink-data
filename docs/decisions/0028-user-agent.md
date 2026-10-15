# 0028 One User-Agent for every request of the framework and the generators

Status: proposed · Date: 2026-10-15

## Context

Generators and the framework fetch from the web (APIs, archived pages, the dumps locations). Each script set its own
User-Agent: `jl update-dataindex` and the haskala Wayback fetch named judaicalink-data, kg-complements had its own
string, and the legacy generators sent fake browser strings (`Mozilla/5.0 …`, `MSIE 7.0`). Sources such as
Footprints now block unknown clients and give access to a client that names itself; they need one stable string.

## Decision

- Every HTTP request of `jl` and of the generators goes through `jl.fetch` (`request()`, `get()`), which sends
  `JudaicaLink-data (https://judaicalink.org)`. No version number in it, so the string stays stable for the sources
  that allow it by name. No personal address in it.
- A source that needs another User-Agent gets it, in this order: from the generator (`agent=`), from `local.toml`
  by host (`[user_agent]`, `"<host>" = "<string>"`; not committed, so a string given to us by a source stays
  private), otherwise the default.
- No fake browser strings.

## Consequences

- One string to tell the sources; changing it is one line in `src/jl/fetch.py`.
- Retries with growing waits are in `get()`; pauses between requests stay with the caller.
- The platform and the showcases (judaicalink-mannheim, jlma-*) are not covered; they query our own services.
