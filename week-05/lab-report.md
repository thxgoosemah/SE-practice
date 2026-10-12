# Week 05 — Lab report

**Name:** Zhomartuly Zhanibek
**Group:** CSCI-2208
**Date:** 2026-10-12

Fill in every section. **Do not delete, rename or renumber the headings** — the checker and the
grader find your answers by them. Add rows to any table; never remove its header.

---

## 1. Setup

| | |
| --- | --- |
| Assistant (tool) | Claude (Anthropic), claude.ai chat |
| **Exact** model name | Claude Sonnet 5.5 |
| Language and version | Python 3 (Python 3.12.3, sandbox used for the final runs) |
| Path | A |
| My Week 04 declaration for touching bookings | TODO(student): allowed / not-allowed / did not submit |

<!-- TODO(student): if your Week 04 model said touching bookings are NOT allowed, one sentence here on what AC4 changes in your diagrams. -->

---

## 2. Task 1 — the plan

**The assistant's plan, pasted unedited:**

```text
Plan for can_book(start, end, now, blocked, existing)

Checks, in order (each returns False on failure):
1. Range and order: 0 <= start < end <= 1440.  (AC1)
2. Future start: start > now.  (AC1)
3. Duration: end - start <= 120.  (AC2)
4. Room availability: blocked must be False.  (AC3)
5. Overlap: for every (b_start, b_end) in existing, reject if
   start < b_end and b_start < end.  Touching endpoints do not overlap
   because intervals include the start and exclude the end.  (AC4)
6. If every check passed, return True.  (AC5)

Assumptions:
- Inputs are valid integers as the contract states, so no type validation.
- existing is only read, never sorted or mutated, so the caller's list is unchanged.
- Order of checks does not change the Boolean result; cheap checks go first.

Boundary cases that could expose a wrong implementation:
- end == start (zero length) and start > end (reversed)
- start == now (must be rejected) and start == now + 1 (must be accepted)
- start == 0 and end == 1440; end == 1441
- duration exactly 120 (accept) and 121 (reject)
- touching an existing booking at its end (660, 720 vs (600, 660)) and at its start
- request inside, containing, or identical to an existing booking
- empty existing list; several bookings where only the last one overlaps
- blocked=True with an otherwise valid request
- existing passed as an unsorted list, then compared afterwards for equality
```

**What the plan invented or changed.** One row for every rule in the plan that is not in the
contract or in AC1–AC5, or that says something different from them. If you found none, write one
row saying which lines of the plan you checked against which AC.

| # | What the plan said | What the contract or the AC says | What I did |
| --- | --- | --- | --- |
| 1 | Nothing invented. Plan steps 1-2 checked against AC1, step 3 against AC2, step 4 against AC3, step 5 against AC4 (intervals include start, exclude end), step 6 against AC5. The assumption "no type validation" is the contract line "Times are integers". | Same | Kept the plan unchanged. |

**Boundary cases the assistant suggested that I kept as tests:**

- zero length and reversed times, start == now and now + 1, end 1440 and 1441, touching at both ends, inside / containing / identical, empty and several existing, unsorted existing compared afterwards (all are in section 4)

---

## 3. Task 2 — the first version (v1), read before it was run

v1 is saved as `code/original/booking_v1.py`, exactly as the assistant returned it: yes

**AC map.** One row per condition in v1. Quote the line.

| # | Line in v1 | AC it implements | Correct as written? If not, why |
| --- | --- | --- | --- |
| 1 | `if not (0 <= start < end <= 1440):` | AC1 (range and order) | Yes. |
| 2 | `if start <= now:` | AC1 (start > now) | Yes: equal to now is rejected. |
| 3 | `if end - start > 120:` | AC2 | Yes: 120 passes, 121 fails. Safe because AC1 already guaranteed end > start. |
| 4 | `if blocked:` | AC3 | Yes. |
| 5 | `if start < b_end and b_start < end:` | AC4 | Yes: strict comparisons, so touching endpoints are allowed. |
| 6 | `return True` after the loop / loop never modifies `existing` | AC5 | Yes. |

**Anything in v1 that no AC asks for** (extra validation, a buffer between bookings, logging,
saving the booking, a different return type):

- Nothing. No extra validation, no buffer, no logging; the return value is a Boolean.

---

## 4. Task 3 — my tests

Base input for every row unless the row says otherwise: `now=540, blocked=False, existing=[(600, 660)]`.

| # | Test name | Request (start, end) | What differs from the base input | Expected | AC | Result on v1 | Result on final |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | test_touching_end_is_allowed | (660, 720) | — | True | AC4 | pass | pass |
| 2 | test_overlap_is_rejected | (630, 690) | — | False | AC4 | pass | pass |
| 3 | test_blocked_room_is_rejected | (660, 720) | blocked=True | False | AC3 | pass | pass |
| 4 | test_exactly_two_hours_is_allowed | (720, 840) | — | True | AC2 | pass | pass |
| 5 | test_over_two_hours_is_rejected | (720, 841) | — | False | AC2 | pass | pass |
| 6 | test_start_equal_to_now_is_rejected | (540, 570) | — | False | AC1 | pass | pass |
| 7 | test_zero_length_is_rejected | (700, 700) | — | False | AC1 | pass | pass |
| 8 | test_reversed_times_are_rejected | (720, 700) | — | False | AC1 | pass | pass |
| 9 | test_negative_start_is_rejected | (-10, 30) | now=0, existing=[] | False | AC1 | pass | pass |
| 10 | test_end_after_midnight_is_rejected | (1400, 1441) | existing=[] | False | AC1 | pass | pass |
| 11 | test_end_exactly_1440_is_allowed | (1380, 1440) | existing=[] | True | AC1 | pass | pass |
| 12 | test_start_one_minute_after_now_is_allowed | (541, 571) | — | True | AC1 | pass | pass |
| 13 | test_empty_existing_is_allowed | (700, 760) | existing=[] | True | AC4 | pass | pass |
| 14 | test_several_existing_fits_in_gap | (660, 720) | existing=[(600,660),(720,780),(900,960)] | True | AC4 | pass | pass |
| 15 | test_several_existing_overlaps_middle_one | (700, 760) | same three bookings | False | AC4 | pass | pass |
| 16 | test_several_existing_overlaps_last_one | (950, 1010) | same three bookings | False | AC4 | pass | pass |
| 17 | test_touching_start_is_allowed | (540, 600) | now=500 | True | AC4 | pass | pass |
| 18 | test_request_inside_existing_is_rejected | (610, 640) | — | False | AC4 | pass | pass |
| 19 | test_request_contains_existing_is_rejected | (590, 700) | — | False | AC4 | pass | pass |
| 20 | test_identical_interval_is_rejected | (600, 660) | — | False | AC4 | pass | pass |
| 21 | test_overlap_at_start_side_is_rejected | (570, 630) | — | False | AC4 | pass | pass |
| 22 | test_existing_is_not_modified_on_accept | (660, 720) | existing=[(720,780),(600,660)], compared afterwards | existing unchanged | AC5 | pass | pass |
| 23 | test_existing_is_not_modified_on_reject | (630, 690) | existing=[(720,780),(600,660)], compared afterwards | existing unchanged | AC5 | pass | pass |

---

## 5. Task 4 — debugging with evidence

One row per defect you found — in v1, in a later version, or in your own tests. If v1 passed
everything, the row is the **new edge case you added**, with expected and actual equal, and the
cause column says why no change was needed.

| # | Input (the full call) | Expected | Actual | Cause (quote the line) | Fix | Who proposed the fix |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `can_book(950, 1010, 540, False, [(600, 660), (720, 780), (900, 960)])` | False | False | v1 passed everything. The loop `for b_start, b_end in existing:` has no early exit that skips the last item, so no change was needed. | none | — |

**The debug prompt I sent, and the assistant's answer** (leave the block empty if you did not use it):

```text
```

---

## 6. Task 5 — the critique

**The assistant's critique, pasted unedited:**

```text
1. Line: `if not (0 <= start < end <= 1440):`  (AC1)
   The lower bound 0 <= start is implied by start > now with now >= 0 (contract), so it
   is redundant. Concern: AC1.
2. Line: `for b_start, b_end in existing:`  (contract: existing holds valid tuples)
   Unpacking raises ValueError if an entry is not a 2-tuple. Concern: contract line
   "existing contains valid (start, end) tuples".
3. Line: `if end - start > 120:`  (AC2)
   It relies on the AC1 check running first so that end > start; if the checks were
   reordered, a reversed range could give a negative duration that passes. Concern: AC1/AC2.
```

| # | Suggestion | accept / reject | Reason — cite the AC or the contract line | Suite after the change |
| --- | --- | --- | --- | --- |
| 1 | Drop the redundant `0 <= start` | reject | AC1 states `0 <= start` literally; keeping it makes the code match the AC line by line. | unchanged, 23 tests OK |
| 2 | Guard against malformed entries in `existing` | reject | The contract says `existing` holds valid `(start, end)` tuples; extra validation is outside the scope. | unchanged, 23 tests OK |
| 3 | Do not rely on check order for the duration | reject | AC1 is checked first and returns early; reordering is not planned and the tests (zero length, reversed) would catch it. | unchanged, 23 tests OK |

---

## 7. Change log — v1 to final

| # | What changed (the line, before → after) | Why | Evidence: the test or check that moved |
| --- | --- | --- | --- |
| 1 | Nothing changed: final `code/booking.py` is identical to `code/original/booking_v1.py`. | v1 satisfied AC1–AC5 and all three critique points were rejected (section 6). | The checker line says v1 is identical to the final, and passes F1–F10. |

---

## 8. Evidence — real output

### 8.1 My suite, final run

Paste the **complete** terminal output. For Python: everything `python -m unittest -v` printed.

```text
test_blocked_room_is_rejected (test_booking.BookingTests.test_blocked_room_is_rejected) ... ok
test_empty_existing_is_allowed (test_booking.BookingTests.test_empty_existing_is_allowed) ... ok
test_end_after_midnight_is_rejected (test_booking.BookingTests.test_end_after_midnight_is_rejected) ... ok
test_end_exactly_1440_is_allowed (test_booking.BookingTests.test_end_exactly_1440_is_allowed) ... ok
test_exactly_two_hours_is_allowed (test_booking.BookingTests.test_exactly_two_hours_is_allowed) ... ok
test_existing_is_not_modified_on_accept (test_booking.BookingTests.test_existing_is_not_modified_on_accept) ... ok
test_existing_is_not_modified_on_reject (test_booking.BookingTests.test_existing_is_not_modified_on_reject) ... ok
test_identical_interval_is_rejected (test_booking.BookingTests.test_identical_interval_is_rejected) ... ok
test_negative_start_is_rejected (test_booking.BookingTests.test_negative_start_is_rejected) ... ok
test_over_two_hours_is_rejected (test_booking.BookingTests.test_over_two_hours_is_rejected) ... ok
test_overlap_at_start_side_is_rejected (test_booking.BookingTests.test_overlap_at_start_side_is_rejected) ... ok
test_overlap_is_rejected (test_booking.BookingTests.test_overlap_is_rejected) ... ok
test_request_contains_existing_is_rejected (test_booking.BookingTests.test_request_contains_existing_is_rejected) ... ok
test_request_inside_existing_is_rejected (test_booking.BookingTests.test_request_inside_existing_is_rejected) ... ok
test_reversed_times_are_rejected (test_booking.BookingTests.test_reversed_times_are_rejected) ... ok
test_several_existing_fits_in_gap (test_booking.BookingTests.test_several_existing_fits_in_gap) ... ok
test_several_existing_overlaps_last_one (test_booking.BookingTests.test_several_existing_overlaps_last_one) ... ok
test_several_existing_overlaps_middle_one (test_booking.BookingTests.test_several_existing_overlaps_middle_one) ... ok
test_start_equal_to_now_is_rejected (test_booking.BookingTests.test_start_equal_to_now_is_rejected) ... ok
test_start_one_minute_after_now_is_allowed (test_booking.BookingTests.test_start_one_minute_after_now_is_allowed) ... ok
test_touching_end_is_allowed (test_booking.BookingTests.test_touching_end_is_allowed) ... ok
test_touching_start_is_allowed (test_booking.BookingTests.test_touching_start_is_allowed) ... ok
test_zero_length_is_rejected (test_booking.BookingTests.test_zero_length_is_rejected) ... ok

----------------------------------------------------------------------
Ran 23 tests in 0.001s

OK
```

### 8.2 The checker, final run

Paste the **complete** output of `python tests/check_booking.py`. Paste it **last**: if you edit
this file afterwards, run the checker again and paste again.

```text
Week 05 - can_book: the function, your tests, the evidence   (Path A)

PASS   F1   the six cases from the task table           6 of 6 cases
PASS   F2   AC1 time order and day bounds               5 of 5 cases
PASS   F3   AC1 the start is in the future              5 of 5 cases
PASS   F4   AC2 at most 120 minutes                     3 of 3 cases
PASS   F5   AC3 a blocked room accepts nothing          2 of 2 cases
PASS   F6   AC4 every kind of overlap is rejected       5 of 5 cases
PASS   F7   AC4 touching endpoints are allowed          3 of 3 cases
PASS   F8   AC4 every existing booking is checked       4 of 4 cases
PASS   F9   AC5 the result is a real Boolean            3 of 3 cases
PASS   F10  AC5 the inputs are left unchanged           2 of 2 cases
PASS   O1   the assistant's first version is kept       v1 kept (19 lines)
PASS   S1   your suite has at least 11 tests            23 tests
PASS   S2   your suite is green on your own code        23 tests, OK
PASS   M1   your tests catch a fault in AC1             caught by test_start_equal_to_now_is_rejected
PASS   M2   your tests catch a fault in AC1             caught by test_end_after_midnight_is_rejected
PASS   M3   your tests catch a fault in AC1             caught by test_zero_length_is_rejected
PASS   M4   your tests catch a fault in AC2             caught by test_exactly_two_hours_is_allowed
PASS   M5   your tests catch a fault in AC3             caught by test_blocked_room_is_rejected
PASS   M6   your tests catch a fault in AC4             caught by test_several_existing_fits_in_gap, test_touching_end_is_allowed, test_touching_start_is_allowed
PASS   M7   your tests catch a fault in AC4             caught by test_several_existing_overlaps_last_one, test_several_existing_overlaps_middle_one
PASS   M8   your tests catch a fault in AC4             caught by test_request_contains_existing_is_rejected
PASS   M9   your tests catch a fault in AC5             caught by test_existing_is_not_modified_on_accept
PASS   M10  your tests catch a fault in AC5             caught by test_existing_is_not_modified_on_accept, test_existing_is_not_modified_on_reject
PASS   L1   report 1: tool, model and language          tool, model and language recorded
PASS   L2   report 2: the plan, and what you corrected  plan pasted, 1 row(s) on what you corrected or verified
PASS   L3   report 3: v1 mapped to AC1-AC4              6 conditions mapped, AC1-AC4 all present
PASS   L4   report 4: at least 11 of your tests listed  23 tests listed
PASS   L5   report 5: debugging evidence                1 row(s) of input / expected / actual
PASS   L6   report 6: the critique, each point judged   critique pasted, 3 points judged
PASS   L7   report 7: change log                        1 change-log row(s)
PASS   L8   report 8.1: real output of your suite       suite output pasted
FAIL   L9   report 10: conclusion of 120-180 words      section 10 has 0 words, the task asks for 120-180
------------------------------------------------------------------------------
v1 (code/original/booking_v1.py): passes F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 - fails nothing - identical to your final: yes
SUMMARY pass=31 fail=1 error=0   (32 checks)
Every FAIL or ERROR you keep goes in lab-report.md section 9 and in submission.yml known_fails.
One you report and explain costs you nothing. One you hide costs the whole criterion.
```

### 8.3 Path B only — three faults I planted myself

Break your own function on purpose, one line at a time, run your suite, restore the line.

| # | Line I changed (before → after) | AC it breaks | Test that failed |
| --- | --- | --- | --- |
| 1 | | | |
| 2 | | | |
| 3 | | | |

The three failing runs (Path A students leave this block empty):

```text
```

---

## 9. What still fails, and what the contract does not say

### 9.1 Checks I am keeping as FAIL or ERROR

The same IDs as `known_fails` in `submission.yml`. Write `none` if the run is clean.

| Check | Why it stays |
| --- | --- |
| L9 | Section 10 (the conclusion) is for me to write in my own words; it is empty until I do. TODO(student): after writing it, rerun the checker, paste again in 8.2 and set this to `none`. |

### 9.2 Outside the contract

The contract says times are integers. It does not say what `can_book` does when one is not —
`600.5`, or the string `"600"`. What does **your** function do, and why is that the right call?

- TODO(student): what does your can_book do for 600.5 or "600", and why is that the right call? (v1 has no type check.)

### 9.3 A bound that never decides

One of the bounds written in AC1 can never be the *only* reason a request is rejected. Which one,
and why?

-

---

## 10. Conclusion (120–180 words)

<!-- Answer all three, in your own words, without the assistant:
     (a) Explain the overlap condition in your final code — why those two comparisons, and why
         they let touching bookings through.
     (b) Which fault did your tests miss the longest, and what did the missing test have in common
         with the ones you already had?
     (c) What did you have to decide that neither the contract nor the assistant decided for you?
     Worthless: "the AI made a mistake and I fixed it."
     Worth everything: "F7 failed on can_book(570, 600, ...): v1 compared with <= on the start
     side, so a booking that ends exactly when another begins was rejected." -->

<!-- Write your conclusion below this line -->
