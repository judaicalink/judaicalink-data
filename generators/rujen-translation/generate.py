"""rujen-translation: a new version made from the version 2020-09-28 with one systematic error fixed (decision 0024).

Fix (parameter drop_untranslated, default on): 293 abstracts (147 en, 146 de) are not translations but the printed
result object of the translation client, "Translated(src=en, dest=de, text=<the Russian original>, ...)": the source
language was detected wrongly, nothing was translated (the bug fixed in the labs generator af59323, after the run).
They are dropped; the Russian original is in rujen. The translation caches that could make them again are not in the
inputs area (labs VM, private backup), and a new run of the service would not be reproducible. The label files are
copied unchanged; with the fix off, all files are the same as in 2020-09-28.
"""

import shutil

from jl.rdf import Literal

INPUTS = {"previous": "rujen-translation/2020-09-28"}
PARAMS = {"drop_untranslated": True}

ABSTRACTS = {"rujen-en-abstract-translations.ttl", "rujen-de-abstract-translations.ttl"}


def generate(run):
    for path in run.inputs("previous"):
        if not run.params["drop_untranslated"] or path.name not in ABSTRACTS:
            shutil.copyfile(path, run.path(path.name))
            continue
        out, dropped = set(), 0
        for s, p, o in run.triples("previous", file=path.name):
            if isinstance(o, Literal) and o.value.startswith("Translated(src="):
                dropped += 1
                continue
            out.add((s, p, o))
        run.note(f"{path.name}: {dropped} untranslated abstracts dropped, {len(out):,} triples kept.")
        run.write_turtle(path.name, out)
