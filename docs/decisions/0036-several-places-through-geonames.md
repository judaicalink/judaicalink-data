# 0036 Places joined through GeoNames may hold several records of one dataset

Status: accepted · Date: 2026-10-26 · Amends [0032](0032-identity-declarations.md)

## Context

The entity pages join at most one current record of each record dataset (0032): a second record of the same
dataset on one entity is a duplicate or a wrong link, and the less trusted link that would make it is refused. For
places this rule refuses joins we want. Footprints has two records for Breslau, Bad Homburg, Offenbach and others,
one with the GeoNames id of the city and one with that of the administrative unit of the same name, or two records
of one place. GeoNames keeps a city, its municipality and its district apart; we do not (0032: several features of
one entity are kept). In ep 2026-10-26 the rule refused 14 such links of footprints, and the second record and the
administrative unit got a page of their own.

## Decision

- A union through a GeoNames key may bring several records of one dataset onto one entity if all of these records
  are places (class `Place`). Other unions keep the rule: a later link through GND, Wikidata or another key that
  would add a further record of that dataset is refused as before.
- The ep run counts and logs these joins ("several places: …"), as it logs the refused links.
- Not covered: organisations with a GeoNames id (e.g. the GND records of the Auschwitz camp and of Birkenau,
  joined through Wikidata and GeoNames) keep the rule.
