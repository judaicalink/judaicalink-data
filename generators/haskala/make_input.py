"""Make the input inputs:haskala/drupal-2015-04-20 from the complete database dump of the Library of Haskala.

python3 make_input.py <haskala.sql> <out.sql.gz>

The source is research/haskala.sql of github.com/judaicalink/haskala (the mysqldump of the Drupal 7 database of
haskala-library.net at its host Pantheon, completed 2015-04-20). Only the tables of the allow-list are copied, each
section (structure and data) byte for byte with the header and footer of the dump: the content (nodes, field data,
taxonomies, page addresses), its schema (node types, field definitions, text formats), the migration maps (the record
ids of the research database the site was migrated from) and the search configuration. Left out: user accounts,
roles, sessions, logs, caches, site settings and the search server (personal data, credentials), and the tables that
repeat or index the content (field_revision_*, node_revision with one revision per node, taxonomy_index,
search_api_item) or only run the site (menus, blocks, registry, system).
"""

import gzip
import re
import sys

KEEP = {"node", "node_type", "field_config", "field_config_instance", "taxonomy_vocabulary", "taxonomy_term_data",
        "taxonomy_term_hierarchy", "url_alias", "filter_format", "filter", "search_api_index", "search_api_page",
        "migrate_status"}
KEEP_PREFIX = ("field_data_", "migrate_map_")
MARK = "--\n-- Table structure for table `"


def main(src, out):
    text = open(src, encoding="utf-8").read()
    first = text.index(MARK)
    end = text.rindex("UNLOCK TABLES;\n") + len("UNLOCK TABLES;\n")
    head, body, foot = text[:first], text[first:end], text[end:]
    sections = [MARK + s for s in body[len(MARK):].split("\n" + MARK)]
    kept, left = [], []
    for s in sections:
        name = re.match(r"--\n-- Table structure for table `([^`]+)`", s).group(1)
        (kept if name in KEEP or name.startswith(KEEP_PREFIX) else left).append((name, s))
    with gzip.GzipFile(out, "wb", mtime=0) as f:
        f.write((head + "\n".join(s.rstrip("\n") + "\n" for _n, s in kept) + foot).encode("utf-8"))
    print(f"{len(kept)} tables kept, {len(left)} left out: {', '.join(n for n, _s in left)}")


if __name__ == "__main__":
    main(*sys.argv[1:])
