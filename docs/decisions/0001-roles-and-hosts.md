# 0001 Roles: Frankfurt runs, Mannheim develops; mannheim.judaicalink.org

Status: accepted · Date: 2026-10-07

## Context

Since 2025 JudaicaLink runs in the portal of the FID Jewish Studies in Frankfurt (Django applications,
Solr, SPARQL, catalogue, `data.judaicalink.org`). Mannheim continues the development of the knowledge
graph (see web.judaicalink.org/production/). Development needs a place to load, query and show our
version of the data, with own views, without competing with the production service.
`labs.judaicalink.org` was that place before the migration; it now forwards to web.judaicalink.org/labs/,
which explains what happened to labs as part of the handover.

## Decision

- **Frankfurt** runs the service: production, curation of what is in production, the official catalogue,
  user support, `data.judaicalink.org`.
- **Mannheim** develops: data generation and cleaning, data model, entity pages, provenance, Wikidata,
  demonstrators. Results are offered to Frankfurt, who adopt them by hand. New data from Frankfurt is
  taken over by hand. There is no automated synchronisation in either direction.
- **mannheim.judaicalink.org** is the Mannheim platform for the further technical development of the
  knowledge graph and for demonstrators: our version of the graph (SPARQL), our newer dumps, the
  complete catalogue of our data version, demonstrators (dashboard, entity-page search, ...).
- **labs.judaicalink.org is not reused**: its nature changed, and its forward to the explanation page is
  part of the handover.
- **judaicalink.ki.hs-mannheim.de** is only the technical name of the VM (141.19.143.18) and is never used
  publicly. Nothing on mannheim.judaicalink.org may depend on the grown setup of that VM: everything must
  be reproducible on a clean VM from the repositories.
- **web.judaicalink.org** stays the project website with its editorial line (see the `CLAUDE.md` of
  `judaicalink-site`): it points users to Frankfurt and presents the Mannheim work.

## Consequences

- Demonstrators are self-contained (ideally one Python file plus static assets) and can produce their own
  HTML views; whether a pubby-like Linked Data frontend is set up on mannheim.judaicalink.org is open and
  will follow the needs of the work.
- Deployment of mannheim.judaicalink.org is scripted and documented in the repositories.
