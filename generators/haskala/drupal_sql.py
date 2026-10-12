"""Read a MySQL dump (Sequel Pro / mysqldump) of a Drupal 7 database with the standard library.

tables(path) -> {table: {"columns": [names], "rows": [tuples]}}. Values: int, float, str, bytes (X'..' blobs) or
None. Only CREATE TABLE (for the column order) and INSERT INTO statements are read. php_unserialize reads the
serialized PHP arrays Drupal keeps in blobs (field settings).
"""

import gzip
import re

CREATE = re.compile(r"^CREATE TABLE `([^`]+)` \(")
INSERT = re.compile(r"^INSERT INTO `([^`]+)` (?:\(([^)]*)\) )?")
ESC = {"0": "\0", "n": "\n", "r": "\r", "t": "\t", "Z": "\x1a", "b": "\b"}


def _values(s, i, out):
    """Parse '(v, v, ...),(...)' from s[i:] into out (a list of tuples); return the index after the last tuple."""
    n = len(s)
    while i < n:
        c = s[i]
        if c in " \t\r\n,":
            i += 1
            continue
        if c == ";":
            return i + 1, True
        if c != "(":
            raise ValueError(f"unexpected {s[i:i + 40]!r}")
        i += 1
        row = []
        while True:
            while s[i] in " \t\r\n":
                i += 1
            binary = s.startswith("_binary ", i)
            if binary:
                i += len("_binary ")
            c = s[i]
            if c == "'":
                i += 1
                buf = []
                while True:
                    j = s.find("'", i)
                    k = s.find("\\", i)
                    if k != -1 and k < j:
                        buf.append(s[i:k])
                        e = s[k + 1]
                        buf.append(ESC.get(e, e))
                        i = k + 2
                        continue
                    if s.startswith("''", j):
                        buf.append(s[i:j] + "'")
                        i = j + 2
                        continue
                    buf.append(s[i:j])
                    i = j + 1
                    break
                v = "".join(buf)
                row.append(v.encode("utf-8") if binary else v)
            elif c == "X" and s[i + 1] == "'":
                j = s.find("'", i + 2)
                row.append(bytes.fromhex(s[i + 2:j]))
                i = j + 1
            else:
                m = re.compile(r"NULL|-?[0-9]+(?:\.[0-9]+)?(?:[eE][-+]?[0-9]+)?").match(s, i)
                if not m:
                    raise ValueError(f"unexpected value {s[i:i + 40]!r}")
                t = m.group(0)
                row.append(None if t == "NULL" else float(t) if any(x in t for x in ".eE") else int(t))
                i = m.end()
            while s[i] in " \t\r\n":
                i += 1
            if s[i] == ",":
                i += 1
                continue
            if s[i] == ")":
                i += 1
                out.append(tuple(row))
                break
            raise ValueError(f"unexpected {s[i:i + 40]!r}")
    return i, False


def tables(path, skip=()):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:
        text = f.read()
    result = {}
    pos = 0
    lines = iter(re.finditer(r"^(CREATE TABLE|INSERT INTO) `([^`]+)`[^\n]*$", text, re.M))
    for m in lines:
        name = m.group(2)
        if name in skip:
            continue
        if m.group(1) == "CREATE TABLE":
            result[name] = {"columns": [], "rows": []}
            end = text.find("\n)", m.end())
            for col in re.finditer(r"^\s+`([^`]+)` ", text[m.end():end], re.M):
                result[name]["columns"].append(col.group(1))
            continue
        listed = INSERT.match(m.group(0)).group(2)
        if listed is not None and [c.strip(" `") for c in listed.split(",")] != result[name]["columns"]:
            raise ValueError(f"{name}: INSERT columns differ from CREATE TABLE")
        i = text.index("VALUES", m.start()) + len("VALUES")
        pos, done = _values(text, i, result[name]["rows"])
        if not done:
            raise ValueError(f"{name}: INSERT without its end")
    return result


def php_unserialize(b):
    """A serialized PHP value (bytes or str) as Python (arrays become dicts)."""
    if isinstance(b, str):
        b = b.encode("utf-8")
    def val(i):
        t = b[i:i + 1]
        if t == b"N":
            return None, i + 2
        if t in (b"i", b"b", b"d"):
            j = b.index(b";", i)
            v = b[i + 2:j].decode()
            return (int(v) if t == b"i" else bool(int(v)) if t == b"b" else float(v)), j + 1
        if t == b"s":
            j = b.index(b":", i + 2)
            n = int(b[i + 2:j])
            return b[j + 2:j + 2 + n].decode("utf-8"), j + 2 + n + 2
        if t == b"a":
            j = b.index(b":", i + 2)
            n = int(b[i + 2:j])
            i = j + 2
            d = {}
            for _ in range(n):
                k, i = val(i)
                v, i = val(i)
                d[k] = v
            return d, i + 1
        raise ValueError(f"PHP value {b[i:i + 20]!r}")
    return val(0)[0]
