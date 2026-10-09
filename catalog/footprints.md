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

[[versions]]
version = "2024-03-18"
issued = "2024-03-18"
author = "Christian Deuschle"
graph = "http://data.judaicalink.org/data/footprints"
description = "Generated with the footprints generator (judaicalink-generators); the published version until 2026 was the regeneration of 2025-03-21, which contains only the names."

  [[versions.files]]
  path = "footprints.ttl.gz"
  bytes = 1347325
  sha256 = "a5d06cb5f3c5aee2216f7cae92060a194d1598730ecd7f822f50f01ab4781deb"

[[changelog]]
date = "2025-03-21"
author = "Benjamin Schnabel"
text = "Generator revised and dataset regenerated; that version contained only the names and is not kept."

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
