"""2014links: a new version made from the version 2017-02-15 with one systematic error fixed (decision 0024).

The Silk runs of 2014 cannot be run again (README), so this generator transforms the previous version. Fix (parameter
drop_person_place_links, default on): the links of rujen were found by matching names, also those of rujen persons
whose name is the name of a place (Fanny Berlin, Mikhail Lvov, Paul Marselle, Yakov Lyubin, ...), which were linked
to the places of DBpedia, LinkedGeoData and DM2E; every link from a record that rujen types as a person to a place is
dropped (found 2026-10-12 with the entity-page closure, decision 0022). The other files are copied unchanged; with the
fix off, all files are the same as in 2017-02-15.
"""

import gzip
import os
import shutil

from jl.rdf import RDF_TYPE, nt_line

INPUTS = {"previous": "2014links/2017-02-15", "rujen": "rujen/2020-09-28"}
PARAMS = {"drop_person_place_links": True}
CORRECTIONS = False   # a transformation of the files of the previous version, as they are

JLO = "http://data.judaicalink.org/ontology/"
PLACE_FILES = {"rujenDBpediaPlace.nt.gz", "rujenLGDOPlace.nt.gz"}   # all their targets are places
DM2E_PLACE = "http://data.dm2e.eu/data/place/"


def is_place_link(file, o):
    return file in PLACE_FILES or (file == "rujenDM2E.nt.gz" and o.startswith(DM2E_PLACE))


def generate(run):
    persons = {s for s, p, o in run.triples("rujen") if p == RDF_TYPE and o == JLO + "Person"}
    base = run.inputs("previous")[0].parent.parent   # <store>/2014links/2017-02-15
    for path in run.inputs("previous"):
        rel = path.relative_to(base).as_posix()
        dst = run.path(rel)
        if not run.params["drop_person_place_links"] or not path.name.startswith("rujen"):
            shutil.copyfile(path, dst)
            continue
        kept, dropped = [], 0
        for s, p, o in run.triples("previous", file=path.name):
            if s in persons and is_place_link(path.name, o):
                dropped += 1
                continue
            kept.append(nt_line(s, p, o))
        if not dropped:
            shutil.copyfile(path, dst)
            continue
        tmp = dst.with_name(dst.name + ".tmp")
        with open(tmp, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as f:
            f.write(("\n".join(sorted(set(kept))) + "\n").encode("utf-8"))
        os.replace(tmp, dst)
        run.note(f"{rel}: {dropped} links of rujen persons to places dropped, {len(set(kept))} kept.")
