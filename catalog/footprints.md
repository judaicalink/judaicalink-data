+++
slug = "footprints"
title = "Footprints - Jewish Books through Time and Place"
author = "Kai Eckert"
date = "2024-03-12"
website = "https://footprints.ctl.columbia.edu/"
example = "http://data.judaicalink.org/data/footprints/0039ddb3-52b5-5644-bd42-a7ab92611d03"
namespaces = ["footprints"]
stable = "2026-09-26"

[license]
name = "CC BY-SA 4.0"
uri = "https://creativecommons.org/licenses/by-sa/4.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-sa.png"

[[versions]]
version = "2026-09-26"
issued = "2024-03-12"
author = "Christian Deuschle"
graph = "http://data.judaicalink.org/data/footprints"
description = "Archived state, identical to the catalogue state judaicalink-site 81b42a5."

  [[versions.files]]
  path = "footprints.ttl.gz"
  bytes = 445278
  sha256 = "01973c29750d5dcb8b9557d75b861639d82d25246140c0c5f696b85b07c3dbe3"

[[changelog]]
date = "2026-10-09"
text = "Migrated to the entry format of decision 0013: one version 2026-09-26 with the files of the archived catalogue state (judaicalink-site 81b42a5)."
refs = ["0013"]
+++
Footprints traces the history and movement of Jewish books since the inception of print. <!--more--> 

The history of the book is an important part of humanities scholarship. Especially as more books are digitized, scholars, librarians, collectors, and others have become increasingly attuned to the significance of individual books as objects with their own unique story. Jewish books in particular tell a fascinating story about the spread of knowledge and faith in a global Diaspora.

Every literary work represents a moment in time and space where an idea was conceived and documented. But the history of a book continues long after composition as it is bought, sold, shared, read, confiscated, stored, or even discarded. This history is the essence of Footprints.

This dataset contains persons (foaf.name, skos.prefLabel, jl.birthDate, jl.deathDate, owl.sameAs [GND,VIAF,LOC],  jl.occupation), books (gndo.author,jl.hasAbstract, gndo.language, gndo.associatedPlace, gndo.dateOfPublication, dc.publisher, gndo.author, gndo.editor, gndo.printer, dc.contributor, gndo.compiler, gndo.translator, gndo.sponsorOrPatron, gndo.dedicatee, jl.hasAbstract, jl.describedAt, gndo.owner, gndo.formerOwner) and places (
gndo.gndIdentifier, jl.describedAt, rdfs.label, skos.prefLabel, geo.asWKT, gndo.hierarchicalSuperiorOfPlaceOrGeographicName)
