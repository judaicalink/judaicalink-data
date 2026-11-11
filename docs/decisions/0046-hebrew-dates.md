# 0046 Hebrew dates are normalised to the Gregorian calendar

Status: accepted · Date: 2026-11-11 · Amends [0035](0035-dates-edtf.md)

## Context

BHR and others give dates as a Hebrew day and month with a year, mostly a Gregorian one: „3. Tischri 1866“,
„16. Tebeth 1871“, Kislew 1836/37. A Hebrew year spans two Gregorian years, Marcheschwan and Kislew have 29 or 30
days, and a leap year has Adar I and Adar II.

## Decision

- The date is converted with the arithmetic Hebrew calendar (Reingold and Dershowitz, `jl.dates`).
- **Which Hebrew year:** a Hebrew year (5000–5800) is taken as written; a Gregorian year is the Hebrew year that puts
  the date into it; a pair (Kislew 1836/37) is the Hebrew year that begins in the first.
- **Without a day:** the month as an EDTF interval (Adar 1858 → 1858-02-15/1858-03-15).
- **Only the year:** where both Hebrew years put the date into the Gregorian year (16 Tevet 1871: 9 January and
  28 December), Adar without I or II in a leap year, or a day that does not exist (30 Tewet 1820).
- Doubts of the source ("?", "vielleicht", "nach Wreschner: …") mark the date uncertain, as "ca." does.

## Consequences

- Checked against the Gregorian dates the texts give beside them: „3. Tischri 1866“ (12. Sept. 1866), „9. Tischri 1843“
  (3. Okt. 1843), „27. Tischri 1797“ (17. Okt. 1797), „19. Schewat 1958“ (8./9. Febr. 1958).
