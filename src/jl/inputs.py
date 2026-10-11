"""The inputs area (decision 0021): inputs of generators that are not published, kept in one place outside the store.

<inputs>/<source>/<name>/ is one input: its files (any layout below the folder) and input.toml, which describes it:

    title = "Compact Memory full text for the Solr core cm_meta (v2)"
    origin = "where it comes from: a URL where there is one, else text (who made or sent it, when)"
    description = "what it is: content, format, how it was made"
    date = "2026-10-05"                  # when it was made or received
    note = "optional: why it is not published, where else it is"

    [files."docs-0000.jsonl.gz"]
    bytes = 58723411
    sha256 = "…"
    description = "optional, for this file"

The files table is written by `jl add-input` and checked by `jl check-inputs`; the texts are edited by hand.
Generators name an input as "inputs:<source>/<name>/" (all its files) or "inputs:<source>/<name>/<path>"; the run
record copies the texts and names every file by its path in the area and its checksum, never by a local path.
"""

import datetime
import json
import shutil
import tomllib
from pathlib import Path

from . import catalog

DESCRIPTION = "input.toml"
TEXTS = ("title", "origin", "description", "date", "note")
IGNORED = {DESCRIPTION, ".DS_Store"}


class InputError(LookupError):
    pass


def toml_str(s):
    return json.dumps(str(s), ensure_ascii=False)


def files_of(folder):
    """The files of an input folder (relative POSIX paths), without input.toml."""
    return sorted(p.relative_to(folder).as_posix() for p in folder.rglob("*")
                  if p.is_file() and p.name not in IGNORED)


def load(root, name):
    """The description of one input: its texts and files."""
    folder = root / name
    p = folder / DESCRIPTION
    if not p.is_file():
        raise InputError(f"inputs:{name}: no {DESCRIPTION} in {folder}")
    try:
        data = tomllib.loads(p.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise InputError(f"inputs:{name}/{DESCRIPTION}: {e}") from None
    for k in ("title", "origin", "description"):
        if not isinstance(data.get(k), str) or not data[k].strip():
            raise InputError(f"inputs:{name}/{DESCRIPTION}: '{k}' is required")
    data["files"] = data.get("files") or {}
    return data


def find(root, ref):
    """'<source>/<name>[/<path>]' -> (name, path or None): the longest leading folder with an input.toml."""
    parts = ref.strip("/").split("/")
    for i in range(len(parts), 0, -1):
        if (root / "/".join(parts[:i]) / DESCRIPTION).is_file():
            rest = "/".join(parts[i:])
            return "/".join(parts[:i]), (rest or None)
    raise InputError(f"inputs:{ref}: no input folder with {DESCRIPTION} in the inputs area")


def write(root, name, texts, files):
    """Write input.toml: the texts in order, then the files (sorted)."""
    lines = [f"{k} = {toml_str(texts[k])}" for k in TEXTS if texts.get(k)]
    for path in sorted(files):
        f = files[path]
        lines += ["", f"[files.{toml_str(path)}]", f"bytes = {f['bytes']}", f"sha256 = {toml_str(f['sha256'])}"]
        if f.get("description"):
            lines.append(f"description = {toml_str(f['description'])}")
    (root / name / DESCRIPTION).write_text("\n".join(lines) + "\n", encoding="utf-8")


def add(root, name, paths, texts, move=False):
    """Put files or folders into the input <name> (created if new) and describe them. A folder keeps its contents'
    relative paths. Returns the files added."""
    if len(name.strip("/").split("/")) != 2:
        raise InputError(f"{name}: give <source>/<name>")
    folder = root / name
    existing = load(root, name) if (folder / DESCRIPTION).is_file() else None
    if existing is None:
        for k in ("title", "origin", "description"):
            if not texts.get(k):
                raise InputError(f"a new input needs --{k}")
    folder.mkdir(parents=True, exist_ok=True)
    added = []
    for src in paths:
        src = Path(src).expanduser()
        if not src.exists():
            raise InputError(f"{src}: does not exist")
        dst = folder / src.name
        if dst.exists():
            raise InputError(f"{dst} exists already")
        if move:
            shutil.move(str(src), str(dst))
        elif src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copyfile(src, dst)
        added.append(src.name)
    data = existing or {}
    merged = {k: texts.get(k) or data.get(k) for k in TEXTS}
    if not merged.get("date"):
        merged["date"] = datetime.date.today().isoformat()
    files = dict(data.get("files", {}))
    for path in files_of(folder):
        if path not in files:
            p = folder / path
            files[path] = {"bytes": p.stat().st_size, "sha256": catalog.sha256(p)}
    write(root, name, merged, files)
    return added


def check(root, verify=True):
    """Check every input of the area: described files present (size, checksum), no file undescribed.
    Returns [(name, number of files, problems)]."""
    out = []
    for desc in sorted(root.rglob(DESCRIPTION)) if root and root.is_dir() else []:
        name = desc.parent.relative_to(root).as_posix()
        problems = []
        try:
            data = load(root, name)
        except InputError as e:
            out.append((name, 0, [str(e)]))
            continue
        present = set(files_of(desc.parent))
        for path, f in data["files"].items():
            p = desc.parent / path
            if path not in present:
                problems.append(f"{path}: missing")
            elif p.stat().st_size != f.get("bytes"):
                problems.append(f"{path}: size differs")
            elif verify and catalog.sha256(p) != f.get("sha256"):
                problems.append(f"{path}: checksum differs")
        for path in sorted(present - set(data["files"])):
            problems.append(f"{path}: not described in {DESCRIPTION}")
        out.append((name, len(data["files"]), problems))
    return out


def resolve(root, ref, verify=True):
    """An input reference 'inputs:<source>/<name>[/<path>]' as (texts of the input, [{ref, file, sha256, bytes,
    path}]); files are checked against input.toml."""
    if root is None:
        raise InputError("'inputs' is not configured in local.toml (decision 0021)")
    name, path = find(root, ref[len("inputs:"):])
    data = load(root, name)
    described = data["files"]
    if path:
        chosen = [p for p in described if p == path or p.startswith(path.rstrip("/") + "/")]
        if not chosen:
            raise InputError(f"{ref}: not a file of inputs:{name}")
    else:
        chosen = sorted(described)
    out = []
    for p in chosen:
        local = root / name / p
        f = described[p]
        if not local.is_file():
            raise InputError(f"inputs:{name}/{p} is missing in the inputs area")
        if local.stat().st_size != f.get("bytes") or (verify and catalog.sha256(local) != f.get("sha256")):
            raise InputError(f"inputs:{name}/{p} differs from {DESCRIPTION}")
        out.append({"ref": f"inputs:{name}/{p}", "file": Path(p).name, "sha256": f["sha256"],
                    "bytes": f["bytes"], "path": local})
    texts = {k: data[k] for k in TEXTS if data.get(k)}
    texts["input"] = f"inputs:{name}"
    return texts, out
