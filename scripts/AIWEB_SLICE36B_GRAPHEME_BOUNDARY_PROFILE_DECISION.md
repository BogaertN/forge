# Slice 36B Grapheme-Boundary Profile Decision

## Decision

Slice 36B uses exact Unicode code-point and UTF-8 byte boundaries for all
captured source. It claims exact grapheme boundaries only under a closed ASCII profile,
with CRLF treated as one cluster boundary sequence.

A boundary touching non-ASCII source is marked `unavailable` rather than being guessed.

## Reason

The Python standard library exposes Unicode categories, names and combining
classes, but not the complete property tables needed to implement current UAX #29 extended grapheme clusters faithfully across all scripts and emoji
sequences. A partial approximation must not be mislabeled as Unicode grapheme
authority.

## Consequence

Non-ASCII material remains fully preserved and reversible at the code-point and
byte levels. Later work may admit a checksum-bound Unicode property resource
and a separately tested grapheme profile. No external resource is admitted by
Slice 36B.
