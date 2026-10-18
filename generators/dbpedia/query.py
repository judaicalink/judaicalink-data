"""Ask Wikipedia for the current articles of the titles our data names (makes the input of dbpedia, decision 0031).

python3 query.py <out dir> [<work dir>] [--use <slug>/<version or run id> …]

1. The titles: every English and German Wikipedia article or DBpedia resource (jl.identifiers: wikipedia-en,
   wikipedia-de) that our datasets name as object and the authority datasets name by a declared identity statement
   (jl.authorities.linking_inputs, as the cascade selects), and the titles of the records of dbpedia-persons (the
   dataset dbpedia replaces). Not articles (left out): titles in the namespaces of categories, files, templates,
   portals and the project itself.
2. Per language the Wikipedia API (action=query, redirects, prop=pageprops with wikibase_item; 50 titles per request,
   maxlag): for each title asked, the normalised title, the redirect followed, the current article (its title and page
   id) or that it is missing, and its Wikidata item. titles-<lang>.jsonl, one line per title asked: {"asked",
   "title" (current; absent if missing), "pageid", "redirect" (the title redirected from), "missing", "invalid",
   "item"}.
Answers are kept per title in the work dir, so an interrupted run continues and a later run asks only for new titles.
One request at a time with a pause; jl.fetch waits on 429/5xx.
"""

import json
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from jl import authorities, catalog, config, generator, identifiers  # noqa: E402
from jl.fetch import get  # noqa: E402
from jl.rdf import read_triples  # noqa: E402

LANGS = {"wikipedia-en": "en", "wikipedia-de": "de"}
API = "https://{}.wikipedia.org/w/api.php"
PAUSE = 1
BATCH = 50
NOT_ARTICLES = {"category", "kategorie", "file", "datei", "image", "bild", "template", "vorlage", "portal",
                "wikipedia", "help", "hilfe", "special", "spezial", "user", "benutzer", "talk", "diskussion",
                "media", "mediawiki", "module", "modul", "draft", "list"}

ARGS, USE = [], []
_it = iter(sys.argv[1:])
for _a in _it:
    if _a == "--use":
        USE.append(next(_it, ""))
    else:
        ARGS.append(_a)


def is_article(title):
    head, sep, _rest = title.partition(":")
    return not (sep and head.strip().lower() in NOT_ARTICLES)


def titles(cfg, cat):
    """{lang: {title}}."""
    generator.USE.update(generator.parse_use(USE))
    refs = dict(authorities.linking_inputs("dbpedia"))
    e = cat.get("dbpedia-persons")
    refs["previous"] = f"dbpedia-persons/{e.stable}"
    generator.USE.clear()
    out = {lang: set() for lang in LANGS.values()}
    for ref in refs.values():
        slug = generator.slug_of(ref)
        for f in generator.resolve(cfg, cat, ref):
            for _s, p, o in read_triples(f["path"]):
                x = identifiers.identify(o, p)
                if x and x[0] in LANGS and identifiers.selects(slug, p, x[0]) and is_article(x[1]):
                    out[LANGS[x[0]]].add(x[1])
        print(f"  {ref}: {sum(len(v) for v in out.values()):,} titles so far", flush=True)
    return out


def ask(lang, batch):
    q = {"action": "query", "format": "json", "formatversion": "2", "redirects": "1", "prop": "pageprops",
         "ppprop": "wikibase_item", "maxlag": "5", "titles": "|".join(t.replace("_", " ") for t in batch)}
    for i in range(6):
        data = json.loads(get(API.format(lang) + "?" + urllib.parse.urlencode(q)))
        if data.get("error", {}).get("code") == "maxlag":
            time.sleep(5 * (i + 1))
            continue
        if "error" in data:
            raise RuntimeError(f"{lang}: {data['error']}")
        return data.get("query", {})
    raise RuntimeError(f"{lang}: maxlag kept up")


def resolve(batch, query):
    """{asked: answer} for a batch: normalisation, then redirect, then the page."""
    norm = {n["from"]: n["to"] for n in query.get("normalized", [])}
    red = {r["from"]: r["to"] for r in query.get("redirects", [])}
    pages = {p["title"]: p for p in query.get("pages", [])}
    out = {}
    for t in batch:
        a = norm.get(t.replace("_", " "), t.replace("_", " "))
        row = {"asked": t}
        if a in red:
            row["redirect"] = a
            a = red[a]
        page = pages.get(a, {})
        if page.get("invalid"):
            row["invalid"] = True
        elif page.get("missing") or "pageid" not in page:
            row["missing"] = True
        else:
            row["title"] = page["title"].replace(" ", "_")
            row["pageid"] = page["pageid"]
            item = page.get("pageprops", {}).get("wikibase_item")
            if item:
                row["item"] = item
        out[t] = row
    return out


def main(out, work):
    out, work = Path(out), Path(work)
    out.mkdir(parents=True, exist_ok=True)
    cfg, cat, t0 = config.load(), catalog.Catalog(), time.time()
    found = titles(cfg, cat)
    for lang, ts in found.items():
        cache_file = work / f"titles-{lang}.jsonl"
        work.mkdir(parents=True, exist_ok=True)
        cache = {}
        if cache_file.is_file():
            for line in cache_file.read_text(encoding="utf-8").splitlines():
                r = json.loads(line)
                cache[r["asked"]] = r
        todo = sorted(t for t in ts if t not in cache)
        print(f"{lang}: {len(ts):,} titles, {len(todo):,} to ask", flush=True)
        with open(cache_file, "a", encoding="utf-8") as c:
            for i in range(0, len(todo), BATCH):
                batch = todo[i:i + BATCH]
                for t, row in resolve(batch, ask(lang, batch)).items():
                    cache[t] = row
                    c.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                c.flush()
                if (i // BATCH) % 20 == 0:
                    print(f"  {lang}: {i + len(batch):,} of {len(todo):,} asked", flush=True)
                time.sleep(PAUSE)
        with open(out / f"titles-{lang}.jsonl", "w", encoding="utf-8") as f:
            for t in sorted(ts):
                f.write(json.dumps(cache[t], ensure_ascii=False, sort_keys=True) + "\n")
    print(f"done: {round(time.time() - t0)} s", flush=True)


if __name__ == "__main__":
    if len(ARGS) not in (1, 2):
        sys.exit(__doc__)
    main(ARGS[0], ARGS[1] if len(ARGS) == 2 else "/Users/kai/lokal/judaicalink/work/dbpedia-query")
