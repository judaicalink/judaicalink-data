# Judging the VIAF numbers of Footprints persons

Footprints (Footprints: Jewish Books Through Time and Place) gives some of its persons a VIAF number. Each line of
the chunk file is one such link: `source` is the Footprints person (its name, the aliases Footprints uses for it, its
class, and what it did: the role in a book record, the title, the date and the place; "printed <date>" is the date of
the imprint), `target` is the VIAF cluster as the dataset viaf has it (class, names, life dates), with the GND record
and Wikidata item the cluster links, where we have them.

Decide for every link whether the Footprints person and the VIAF cluster are the same entity:

- **correct**: the same entity. The names agree (allow transliterations, Hebrew, Latin and other language forms,
  inverted names, patronymics written differently, a missing or added epithet), the kinds agree (a person and a
  person, an institution and an institution), and nothing contradicts; and either the name is distinctive enough or
  the facts tie the two together (life dates fit the activity, the place, the role: a printer, an author of the
  work, an owner who lived when and where the footprint happened). An author may be printed long after his death; a
  printer, publisher, owner, seller or signer must have been active within his lifetime (a few years of slack for
  uncertain dates).
- **wrong**: different entities: a namesake (other dates, other place, other field), a family member (father, son),
  a person for a firm, press, family or institution or the other way round ("the press of X", "X & Sons", "Frères
  X", "Bi-defus X" is a press), a work or a place for a person, a cluster that mixes unrelated persons, or activity
  clearly outside the lifetime (an owner in 1850 linked to a person who died in 1700).
- **undecidable**: too little to tell: a common name (a frequent patronymic, "Moses ben Jacob", "Johannes Luzac") with
  no facts that tie the two together and none that contradict, or a target without names.

Read every link and judge it yourself; do not write a program that decides. Keep the reason short (at most about 15
words, naming the decisive evidence). Write one JSON object per line, in the order of the chunk, to the verdict
file: `{"i": <i>, "verdict": "correct" | "wrong" | "undecidable", "reason": "..."}`.
