"""dbpedia in the cascade of the authority datasets (jl.cascade): Wikipedia asked online, with the cache of query.py.

resolve: the current article of a title (the redirect followed) or None (missing, invalid, or not an article:
query.is_article); the answers are kept per title in <work>/titles-<lang>.jsonl. links: the Wikidata item of the
article (Wikipedia's page property wikibase_item), as the dataset writes it (owl:sameAs). seeds: the static lists,
and the titles of the records of dbpedia-persons (reason "previous"; the dataset replaces it). write: titles-en.jsonl
and titles-de.jsonl of the selected titles, in the format of query.py (the input of the generator).
"""

import json
import time
from pathlib import Path

from jl import identifiers
from jl.cascade import static_seeds
from jl.generator import load_shared, resolve as resolve_ref
from jl.rdf import read_triples

q = load_shared("dbpedia", "query")   # LANGS, is_article, ask, resolve, PAUSE, BATCH

WORK = Path("/Users/kai/lokal/judaicalink/work/dbpedia-query")
SAME = "http://www.w3.org/2002/07/owl#sameAs"
OLD = "http://data.judaicalink.org/data/dbpedia/"
PREVIOUS = "dbpedia-persons/2018-10-24"


class Lookup:
    sources = ("wikipedia-en", "wikipedia-de")
    searched_by = ()

    def __init__(self, cfg, cat, log):
        self.cfg, self.cat, self.log = cfg, cat, log
        WORK.mkdir(parents=True, exist_ok=True)
        self.cache = {}
        for lang in q.LANGS.values():
            rows = {}
            f = WORK / f"titles-{lang}.jsonl"
            if f.is_file():
                for line in f.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        r = json.loads(line)
                        rows[r["asked"]] = r
            self.cache[lang] = rows
        self.items = {lang: {r["title"]: r.get("item") for r in rows.values() if r.get("title")}
                      for lang, rows in self.cache.items()}

    def answers(self, lang, titles):
        """{title: answer row}, asking Wikipedia only for titles not in the cache."""
        rows = self.cache[lang]
        todo = sorted({t for t in titles if t not in rows and q.is_article(t)})
        with open(WORK / f"titles-{lang}.jsonl", "a", encoding="utf-8") as c:
            for k in range(0, len(todo), q.BATCH):
                batch = todo[k:k + q.BATCH]
                for t, row in q.resolve(batch, q.ask(lang, batch)).items():
                    rows[t] = row
                    if row.get("title"):
                        self.items[lang][row["title"]] = row.get("item")
                    c.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                time.sleep(q.PAUSE)
        if todo:
            self.log(f"  dbpedia: {len(todo):,} {lang} titles asked")
        return {t: rows.get(t, {"asked": t, "invalid": True}) for t in titles}

    def seeds(self):
        out = static_seeds(self.cfg, self.cat, "dbpedia")
        langs = {}
        for f in resolve_ref(self.cfg, self.cat, PREVIOUS):
            for s, p, o in read_triples(f["path"]):
                if str(s).startswith(OLD) and p == SAME:
                    x = identifiers.identify(o, p)
                    name = identifiers.wiki_title(str(s)[len(OLD):])
                    if x and x[0] in q.LANGS and x[1] == name and langs.get(str(s)) != "wikipedia-en":
                        langs[str(s)] = x[0]   # the English article where both have the name (as generate.py)
        out += [(src, identifiers.wiki_title(s[len(OLD):]), "previous", PREVIOUS) for s, src in sorted(langs.items())]
        return out

    def resolve(self, source, ids):
        lang = q.LANGS[source]
        rows = self.answers(lang, ids)
        return {t: rows[t].get("title") for t in ids}

    def links(self, source, ids):
        lang = q.LANGS[source]
        missing = [t for t in ids if t not in self.items[lang]]
        rows = self.answers(lang, missing) if missing else {}
        out = {}
        for t in ids:
            item = self.items[lang].get(t) or rows.get(t, {}).get("item")   # an old title: its article's item
            out[t] = {(SAME, "wikidata", item)} if item else set()
        return out

    def write(self, out, selection):
        for source, lang in q.LANGS.items():
            titles = sorted(selection.get(source, {}))
            rows = self.answers(lang, titles)
            with open(Path(out) / f"titles-{lang}.jsonl", "w", encoding="utf-8") as f:
                for t in titles:
                    f.write(json.dumps(rows[t], ensure_ascii=False, sort_keys=True) + "\n")
