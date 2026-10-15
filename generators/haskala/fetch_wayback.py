"""Fetch the archived book pages of haskala-library.net from the Internet Archive (input of the book sections).

python3 fetch_wayback.py <haskala-drupal-2015-04-20.sql.gz> <out dir>

The database does not store how the site grouped the fields of a book page (the sections were part of the site's
code), but the pages show it: every field is a <div class="field field-name-field-..."> inside a section. This
script lists the captures of book pages in the Wayback Machine (CDX API), takes for every book node the earliest
capture with status 200 of its page address, and saves the page as archived (the "id_" form, without the archive's
frame) as book-<node id>.html, with manifest.tsv (node id, address, capture time, archived URL, sha256). One request
per second; the User-Agent is the framework's (decision 0028).
"""

import hashlib
import json
import sys
import time
import unicodedata
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import drupal_sql  # noqa: E402
from jl.fetch import get  # noqa: E402

CDX = ("https://web.archive.org/cdx/search/cdx?url=haskala-library.net/books/&matchType=prefix&output=json"
       "&fl=timestamp,original,statuscode&filter=statuscode:200")


def key(path):
    return unicodedata.normalize("NFC", urllib.parse.unquote(path)).strip("/").lower()


def main(dump, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    t = drupal_sql.tables(dump)
    books = {r[0] for r in t["node"]["rows"] if r[2] == "book"}
    alias = {}
    for pid, source, a, _lang in t["url_alias"]["rows"]:
        if source.startswith("node/") and int(source[5:]) in books:
            alias[key(a)] = int(source[5:])
    rows = json.loads(get(CDX))[1:]
    time.sleep(1)
    first = {}
    for ts, original, _status in rows:
        path = urllib.parse.urlsplit(original).path
        nid = alias.get(key(path))
        if nid is not None and (nid not in first or ts < first[nid][0]):
            first[nid] = (ts, original)
    print(f"{len(rows)} captures, {len(first)} of {len(books)} books archived", flush=True)
    manifest = []
    for nid in sorted(first):
        ts, original = first[nid]
        url = f"https://web.archive.org/web/{ts}id_/{original}"
        path = out / f"book-{nid}.html"
        if not path.exists():
            path.write_bytes(get(url))
            time.sleep(1)
        manifest.append((nid, key(urllib.parse.urlsplit(original).path), ts, url,
                         hashlib.sha256(path.read_bytes()).hexdigest()))
        print(nid, ts, flush=True)
    with open(out / "manifest.tsv", "w", encoding="utf-8") as f:
        f.write("nid\taddress\tcapture\tarchived_url\tsha256\n")
        for row in manifest:
            f.write("\t".join(map(str, row)) + "\n")
    print(f"missing: {sorted(books - set(first))}")


if __name__ == "__main__":
    main(*sys.argv[1:])
