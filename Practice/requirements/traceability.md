# Traceability — use cases → stories → criteria

One row per use case. All six rows stay, even the ones with nothing behind them: an empty cell is a
finding you report, not a failure you hide. Use real IDs, comma-separated; write `none` where there
is nothing.

| Use case | Stories (US-nn) | Criteria (AC-nn) | Gap? |
| --- | --- | --- | --- |
| UC-01 View availability | US-01 | none | Yes — no AC written; US-01 was not one of the 3 stories selected for acceptance criteria. |
| UC-02 Book room | US-02 | AC-01, AC-02, AC-03, AC-04, AC-05 | No |
| UC-03 Cancel booking | US-03 | AC-06, AC-07, AC-08 | No |
| UC-04 Block or unblock room | US-04, US-05 | AC-09, AC-10, AC-11, AC-12 | No |
| UC-05 Review usage | US-06 | none | Yes — no AC written; same reason as UC-01. |
| UC-06 Send confirmation | US-07 | none | Yes — no dedicated AC; it is only exercised indirectly, as the observable "and confirmed" outcome inside AC-01 (book) and AC-06 (cancel). |

**Stories that belong to no use case:** none — every one of US-01…US-07 is listed above.

**What the gaps tell you:** the three uncovered use cases (UC-01, UC-05, UC-06) aren't uncovered
because they're less important — they're uncovered because the assignment scopes acceptance criteria
to only 3 of the 7 stories. UC-06 in particular has no story or use case that "owns" triggering it on
its own; it only ever fires as a side effect of UC-02 or UC-03 succeeding, which is exactly why the
diagram models it with `<<include>>` rather than a direct actor association. The long version of this
reasoning goes in `lab-report.md` §8.
