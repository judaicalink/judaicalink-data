+++
slug = "footprints"
title = "Footprints - Jewish Books through Time and Place"
author = "Kai Eckert"
date = "2024-03-12"
website = "https://footprints.ctl.columbia.edu/"
example = "http://data.judaicalink.org/data/footprints/0039ddb3-52b5-5644-bd42-a7ab92611d03"
namespaces = ["footprints"]
stable = "2024-03-18"

[license]
name = "CC BY-SA 4.0"
uri = "https://creativecommons.org/licenses/by-sa/4.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-sa.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/footprints"

[[versions]]
version = "2025-03-21"
issued = "2025-03-21"
author = "Benjamin Schnabel"
graph = "http://data.judaicalink.org/data/footprints"
description = "Regenerated with a rewritten generator that keeps only the person loop (the book and place sections and the GND, VIAF and translation lookups were dropped, apparently because the old generator no longer ran); contains only the types and names of the resources. 2024-03-18 stays the stable version."

  [[versions.files]]
  path = "footprints.ttl.gz"
  bytes = 445278
  sha256 = "01973c29750d5dcb8b9557d75b861639d82d25246140c0c5f696b85b07c3dbe3"

  [[versions.files]]
  path = "footprints-meta.ttl.gz"
  bytes = 1667
  sha256 = "59c82199c9c13e0107e85d35810adfe83b83d6c37c4cec9c005fed511433ea7f"
  triples = 54

[[versions]]
version = "2024-03-18"
issued = "2024-03-18"
author = "Christian Deuschle"
graph = "http://data.judaicalink.org/data/footprints"
description = "The richer version: books with titles, owners, former owners, places, dates of publication, authors and languages; from the backup of the dumps of 2025-02-06."

  [[versions.files]]
  path = "footprints.ttl.gz"
  bytes = 1347325
  sha256 = "a5d06cb5f3c5aee2216f7cae92060a194d1598730ecd7f822f50f01ab4781deb"

  [[versions.files]]
  path = "footprints-meta.ttl.gz"
  bytes = 1596
  sha256 = "4623d6ac84d346a44941d65a58eb86fb8fa2409828bba4fdca183fd6a6fb9239"
  triples = 54

[[changelog]]
date = "2024-03-12"
author = "Christian Deuschle"
text = "First version, with generator."
+++
Footprints traces the history and movement of Jewish books since the inception of print. <!--more--> 

The history of the book is an important part of humanities scholarship. Especially as more books are digitized, scholars, librarians, collectors, and others have become increasingly attuned to the significance of individual books as objects with their own unique story. Jewish books in particular tell a fascinating story about the spread of knowledge and faith in a global Diaspora.

Every literary work represents a moment in time and space where an idea was conceived and documented. But the history of a book continues long after composition as it is bought, sold, shared, read, confiscated, stored, or even discarded. This history is the essence of Footprints.

This dataset contains persons (foaf.name, skos.prefLabel, jl.birthDate, jl.deathDate, owl.sameAs [GND,VIAF,LOC],  jl.occupation), books (gndo.author,jl.hasAbstract, gndo.language, gndo.associatedPlace, gndo.dateOfPublication, dc.publisher, gndo.author, gndo.editor, gndo.printer, dc.contributor, gndo.compiler, gndo.translator, gndo.sponsorOrPatron, gndo.dedicatee, jl.hasAbstract, jl.describedAt, gndo.owner, gndo.formerOwner) and places (
gndo.gndIdentifier, jl.describedAt, rdfs.label, skos.prefLabel, geo.asWKT, gndo.hierarchicalSuperiorOfPlaceOrGeographicName)
