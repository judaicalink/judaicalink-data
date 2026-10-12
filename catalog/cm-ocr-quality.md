+++
slug = "cm-ocr-quality"
title = "OCR quality estimate for Compact Memory pages"
author = "Kai Eckert"
date = "2026-10-12"
kind = "complement"
method = ["statistical"]
inputs = ["compact-memory"]

[license]
name = "CC0"
uri = "https://creativecommons.org/publicdomain/zero/1.0/"
image = "https://mirrors.creativecommons.org/presskit/buttons/88x31/png/cc-zero.png"

[generator]
repo = "https://github.com/judaicalink/judaicalink-data"
path = "generators/cm-ocr-quality"
+++

An estimate of the OCR quality of every page of Compact Memory, and the mean per journal.

<!--more-->

Per page (`jl:ocrKnownWordShare`): the share of its words (letters only, at least two characters, lowercased) that
occur at least 10 times in every 20th page of the corpus. Per journal (`jl:meanOcrKnownWordShare`): the mean over its
pages. An estimate, not a measurement: Hebrew, Yiddish and Russian pages score lower partly because the word list is
dominated by German. The statements are about the pages and journals of compact-memory; the texts come from the
full text of the FID portal's Compact Memory search.
