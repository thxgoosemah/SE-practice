# Week 05 — Lab report

**Name:** Жағыпар Дидар Қанатұлы

**Group:** CSCI2208

**Date:** 2026-10-11

Fill in every section. **Do not delete, rename or renumber the headings** — the checker and the

grader find your answers by them. Add rows to any table; never remove its header.

---

## 1. Setup

|  |  |
| --- | --- |
| Assistant (tool) | Claude (claude.ai chat, one chat for Tasks 1–5) |
| **Exact** model name | Claude Sonnet 5.5 |
| Language and version | Python 3 |
| Path | A |
| My Week 04 declaration for touching bookings | allowed |

My Week 04 model already allowed touching bookings, so AC4 changes nothing in my Week 04 diagrams.

---

## 2. Task 1 — the plan

**The assistant's plan, pasted unedited:**

```
Implementation plan for can_book (Python 3)

Checks, in order:
1. AC1 range: 0 <= start < end <= 1440. Otherwise return False.
2. AC1 timing: start > now. Otherwise return False.
3. AC2 duration: end - start <= 120. Otherwise return False.
4. AC3 blocked: if blocked is True, return False.
5. AC4 overlap: for each (s, e) in existing, the new interval overlaps when
   start < e and s < end. If any booking overlaps, return False. Touching
   endpoints do not overlap.
6. AC5: if no check failed, return True.

Assumptions:
- Inputs follow the contract (integers, valid now, valid existing tuples), so no extra validation.
- Intervals include the start and exclude the end, so (600, 660) and (660, 720) touch but do not overlap.
- Exactly 120 minutes is allowed (at most 120).
- existing is only read: no sorting, appending or removing. An empty existing means no overlap.
- Only a Boolean is returned; saving and confirmation belong to the complete system.

Boundary cases:
- (660, 720) touching the end of (600, 660): True
- (570, 600) touching the start of (600, 660): True
- (630, 690), (615, 645), (570, 690), (600, 660) overlapping: False
- duration 120: True; duration 121: False
- start == now: False; start == now + 1: True
- start == end, and start > end: False
- end == 1440: True; end == 1441: False
- blocked=True with an otherwise valid request: False
- empty existing; several existing bookings with a conflict only in the last one
- existing identical before and after the call (also when it is unsorted)
```

**What the plan invented or changed.** One row for every rule in the plan that is not in the

contract or in AC1–AC5, or that says something different from them. If you found none, write one

row saying which lines of the plan you checked against which AC.

| # | What the plan said | What the contract or the AC says | What I did |
| --- | --- | --- | --- |
| 1 | None found. I checked steps 1–2 against AC1 (`0 <= start < end <= 1440`, `start > now`), step 3 against AC2, step 4 against AC3, step 5 against AC4 (touching allowed), step 6 against AC5. The assumptions (no extra validation, read-only `existing`, 120 allowed) match the contract lines "now is valid", "existing contains valid tuples", "Keep all inputs unchanged" and AC2. | Same lines as in the left column | Nothing to drop; the plan was kept as is |

**Boundary cases the assistant suggested that I kept as tests:**

- touching end `(660, 720)` and touching start `(570, 600)`
- overlaps `(630, 690)`, `(615, 645)`, `(570, 690)`, `(600, 660)`
- duration 120 and 121
- `start == now` and `start == now + 1`
- zero-length `(700, 700)` and reversed `(800, 700)`
- `end == 1440` and `end == 1441`
- `blocked=True`
- empty `existing`, several `existing` with a conflict only in the last one
- `existing` unchanged after the call (unsorted list)
---

## 3. Task 2 — the first version (v1), read before it was run

v1 is saved as `code/original/booking_v1.py`, exactly as the assistant returned it: yes

**AC map.** One row per condition in v1. Quote the line.

| # | Line in v1 | AC it implements | Correct as written? If not, why |
| --- | --- | --- | --- |
| 1 | `if not (0 <= start < end <= 1440):` | AC1 (day bounds and `start < end`) | Yes. Bounds are inclusive at 0 and 1440 and `start < end` is strict |
| 2 | `if start <= now:` | AC1 (`start > now`) | Yes. `start == now` is rejected, as AC1 says "start > now" |
| 3 | `if end - start > 120:` | AC2 | Yes. Exactly 120 is allowed, 121 is rejected |
| 4 | `if blocked:` | AC3 | Yes |
| 5 | `if start < existing_end and existing_start < end:` | AC4 | Yes. Strict `<` on both sides lets touching endpoints through; the loop checks every booking before `True` |
| 6 | `return True` | AC5 | Yes. Reached only if AC1–AC4 hold; returns the Boolean `True` |

**Anything in v1 that no AC asks for** (extra validation, a buffer between bookings, logging,

saving the booking, a different return type):

- Nothing found. No validation, no buffer, no sorting, no change of `existing`; every return is `True` or `False`.  
**What I expected to fail before running:** nothing in v1. I expected the risk to be in my suite  

(holes against the faulty versions), not in v1.
---

## 4. Task 3 — my tests

Base input for every row unless the row says otherwise: `now=540, blocked=False, existing=[(600, 660)]`.

| # | Test name | Request (start, end) | What differs from the base input | Expected | AC | Result on v1 | Result on final |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | test_touching_end_is_allowed | (660, 720) | — | True | AC4 | pass | pass |
| 2 | test_partial_overlap_rejected | (630, 690) | — | False | AC4 | pass | pass |
| 3 | test_blocked_room_rejected | (660, 720) | blocked=True | False | AC3 | pass | pass |
| 4 | test_exactly_two_hours_allowed | (720, 840) | — | True | AC2 | pass | pass |
| 5 | test_over_two_hours_rejected | (720, 841) | — | False | AC2 | pass | pass |
| 6 | test_start_equal_now_rejected | (540, 570) | — | False | AC1 | pass | pass |
| 7 | test_start_before_now_rejected | (500, 530) | — | False | AC1 | pass | pass |
| 8 | test_start_one_minute_after_now_allowed | (541, 560) | — | True | AC1 | pass | pass |
| 9 | test_zero_length_rejected | (700, 700) | — | False | AC1 | pass | pass |
| 10 | test_reversed_times_rejected | (800, 700) | — | False | AC1 | pass | pass |
| 11 | test_end_at_1440_allowed | (1380, 1440) | — | True | AC1 | pass | pass |
| 12 | test_end_after_1440_rejected | (1380, 1441) | — | False | AC1 | pass | pass |
| 13 | test_empty_existing_allowed | (600, 660) | existing=[] | True | AC4 | pass | pass |
| 14 | test_gap_between_several_bookings_allowed | (780, 840) | existing=[(600,660),(700,760),(900,960)] | True | AC4 | pass | pass |
| 15 | test_overlap_with_last_of_several_rejected | (910, 950) | existing=[(600,660),(700,760),(900,960)] | False | AC4 | pass | pass |
| 16 | test_inside_existing_rejected | (615, 645) | — | False | AC4 | pass | pass |
| 17 | test_contains_existing_rejected | (570, 690) | — | False | AC4 | pass | pass |
| 18 | test_touching_start_is_allowed | (570, 600) | — | True | AC4 | pass | pass |
| 19 | test_identical_interval_rejected | (600, 660) | — | False | AC4 | pass | pass |
| 20 | test_existing_unchanged_when_true | (780, 840) | existing=[(900,960),(600,660),(700,760)] (unsorted); also checks existing equals its copy after the call | True | AC5 | pass | pass |
| 21 | test_existing_unchanged_when_false | (630, 690) | existing=[(900,960),(600,660),(700,760)]; also checks existing equals its copy | False | AC5 | pass | pass |

Every expected value comes from AC1–AC5 and the overlap table, not from running the code.

Each test is built so that only one rule can reject the request (for example `(1380, 1441)` has

duration 61 and no overlap, so only `end <= 1440` rejects it).

---

## 5. Task 4 — debugging with evidence

One row per defect you found — in v1, in a later version, or in your own tests. If v1 passed

everything, the row is the **new edge case you added**, with expected and actual equal, and the

cause column says why no change was needed.

v1 passed all my tests, so this is the "clean v1" case. The extra edge case is a request identical

to an existing booking (my test #19).

| # | Input (the full call) | Expected | Actual | Cause (quote the line) | Fix | Who proposed the fix |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `can_book(600, 660, 540, False, [(600, 660)])` | False | False | `if start < existing_end and existing_start < end:` → 600 < 660 and 600 < 660 is true, so the overlap rule rejects it. No defect, so no change was needed | none | — |

**The debug prompt I sent, and the assistant's answer** (leave the block empty if you did not use it):

```

```

---

## 6. Task 5 — the critique

**The assistant's critique, pasted unedited:**

```
Review of can_book against the contract and AC1-AC5

Result: I found no line that violates AC1-AC5 or the contract. Three observations, none of which is a defect:

1. Line: `if not (0 <= start < end <= 1440):`
   Concerns: AC1.
   The bound `0 <= start` can never be the only reason for a rejection. `now` is valid (0-1439) and the next line requires `start > now`, so any `start < 0` is also rejected by `if start <= now`. The condition is harmless and matches AC1 as written, so no change is needed.

2. Line: `if blocked:`
   Concerns: AC3 and the contract line "blocked is a Boolean".
   The check uses truthiness rather than `blocked is True`. Because the contract guarantees a Boolean, both behave identically here. A stricter comparison would only matter for inputs the contract excludes.

3. Line: `for existing_start, existing_end in existing:`
   Concerns: the contract line "existing contains valid (start, end) tuples" and AC5 ("never alter existing").
   The loop only reads `existing` and examines every booking before `return True`, which satisfies AC4 and AC5. It relies on the contract's guarantee that each entry is a valid tuple; a malformed entry would raise instead of returning False. Under the contract this cannot happen, and adding validation would add a rule no AC asks for.

Everything else maps to one AC each: `end - start > 120` (AC2), `start < existing_end and existing_start < end` (AC4, touching endpoints allowed because both comparisons are strict), `return True` (AC5, returns a Boolean).
```

| # | Suggestion | accept / reject | Reason — cite the AC or the contract line | Suite after the change |
| --- | --- | --- | --- | --- |
| 1 | `0 <= start` в `if not (0 <= start < end <= 1440):` не может быть единственной причиной отказа, потому что `start > now` уже его покрывает | reject | AC1 написано буквально `0 <= start < end <= 1440`; условие безвредно и совпадает с текстом AC1, убирать его нет причины | unchanged, 21 tests OK |
| 2 | В `if blocked:` проверка по истинности вместо `blocked is True` | reject | Контракт: «blocked is a Boolean», при Boolean оба варианта дают один результат; AC3 не требует строгого сравнения | unchanged, 21 tests OK |
| 3 | Цикл `for existing_start, existing_end in existing:` полагается на корректные кортежи; при некорректном элементе будет исключение | reject | Контракт: «existing contains valid (start, end) tuples»; AC5 требует вернуть False, а не исключение, и проверка формата добавила бы правило, которого нет в AC | unchanged, 21 tests OK |

---

## 7. Change log — v1 to final

| # | What changed (the line, before → after) | Why | Evidence: the test or check that moved |
| --- | --- | --- | --- |
| 1 | No change. `booking.py` is identical to `original/booking_v1.py` | v1 passed all 21 of my tests and has one condition per AC; the extra edge case in §5 behaved as expected | All 21 tests pass on v1 and on final; nothing moved |

---

## 8. Evidence — real output

### 8.1 My suite, final run

Paste the **complete** terminal output. For Python: everything `python -m unittest -v` printed (run inside `code/`).

```
PS D:\MyFiles\Study\SE\practices\SE-practice\week-05\code>    python -m unittest -v
test_blocked_room_rejected (test_booking.BookingTests.test_blocked_room_rejected) ... ok
test_contains_existing_rejected (test_booking.BookingTests.test_contains_existing_rejected) ... ok
test_empty_existing_allowed (test_booking.BookingTests.test_empty_existing_allowed) ... ok
test_end_after_1440_rejected (test_booking.BookingTests.test_end_after_1440_rejected) ... ok
test_end_at_1440_allowed (test_booking.BookingTests.test_end_at_1440_allowed) ... ok
test_exactly_two_hours_allowed (test_booking.BookingTests.test_exactly_two_hours_allowed) ... ok
test_existing_unchanged_when_false (test_booking.BookingTests.test_existing_unchanged_when_false) ... ok
test_existing_unchanged_when_true (test_booking.BookingTests.test_existing_unchanged_when_true) ... ok
test_gap_between_several_bookings_allowed (test_booking.BookingTests.test_gap_between_several_bookings_allowed) ... ok
test_identical_interval_rejected (test_booking.BookingTests.test_identical_interval_rejected) ... ok
test_inside_existing_rejected (test_booking.BookingTests.test_inside_existing_rejected) ... ok
test_over_two_hours_rejected (test_booking.BookingTests.test_over_two_hours_rejected) ... ok
test_overlap_with_last_of_several_rejected (test_booking.BookingTests.test_overlap_with_last_of_several_rejected) ... ok
test_partial_overlap_rejected (test_booking.BookingTests.test_partial_overlap_rejected) ... ok
test_reversed_times_rejected (test_booking.BookingTests.test_reversed_times_rejected) ... ok
test_start_before_now_rejected (test_booking.BookingTests.test_start_before_now_rejected) ... ok
test_start_equal_now_rejected (test_booking.BookingTests.test_start_equal_now_rejected) ... ok
test_start_one_minute_after_now_allowed (test_booking.BookingTests.test_start_one_minute_after_now_allowed) ... ok
test_touching_end_is_allowed (test_booking.BookingTests.test_touching_end_is_allowed) ... ok
test_touching_start_is_allowed (test_booking.BookingTests.test_touching_start_is_allowed) ... ok
test_zero_length_rejected (test_booking.BookingTests.test_zero_length_rejected) ... ok

----------------------------------------------------------------------
Ran 21 tests in 0.002s
```

### 8.2 The checker, final run

Paste the **complete** output of `python tests/check_booking.py` (run inside `week-05/`). Paste it **last**: if you edit

this file afterwards, run the checker again and paste again.

```
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
PASS   S1   your suite has at least 11 tests            21 tests
PASS   S2   your suite is green on your own code        21 tests, OK
PASS   M1   your tests catch a fault in AC1             caught by test_start_equal_now_rejected
PASS   M2   your tests catch a fault in AC1             caught by test_end_after_1440_rejected
PASS   M3   your tests catch a fault in AC1             caught by test_zero_length_rejected
PASS   M4   your tests catch a fault in AC2             caught by test_exactly_two_hours_allowed
PASS   M5   your tests catch a fault in AC3             caught by test_blocked_room_rejected
PASS   M6   your tests catch a fault in AC4             caught by test_touching_end_is_allowed, test_touching_start_is_allowed
PASS   M7   your tests catch a fault in AC4             caught by test_existing_unchanged_when_false, test_overlap_with_last_of_several_rejected
PASS   M8   your tests catch a fault in AC4             caught by test_contains_existing_rejected
PASS   M9   your tests catch a fault in AC5             caught by test_existing_unchanged_when_true
PASS   M10  your tests catch a fault in AC5             caught by test_existing_unchanged_when_false, test_existing_unchanged_when_true
PASS   L1   report 1: tool, model and language          tool, model and language recorded
PASS   L2   report 2: the plan, and what you corrected  plan pasted, 1 row(s) on what you corrected or verified
PASS   L3   report 3: v1 mapped to AC1-AC4              6 conditions mapped, AC1-AC4 all present
PASS   L4   report 4: at least 11 of your tests listed  21 tests listed
PASS   L5   report 5: debugging evidence                1 row(s) of input / expected / actual
PASS   L6   report 6: the critique, each point judged   critique pasted, 3 points judged
PASS   L7   report 7: change log                        1 change-log row(s)
FAIL   L8   report 8.1: real output of your suite       section 8.1 needs the complete terminal output of your suite (the part ending in 'Ran N tests ...')
FAIL   L9   report 10: conclusion of 120-180 words      section 10 has 0 words, the task asks for 120-180
------------------------------------------------------------------------------
v1 (code/original/booking_v1.py): passes F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 - fails nothing - identical to your final: yes
SUMMARY pass=30 fail=2 error=0   (32 checks)
Every FAIL or ERROR you keep goes in lab-report.md section 9 and in submission.yml known_fails.
One you report and explain costs you nothing. One you hide costs the whole criterion.
```

### 8.3 Path B only — three faults I planted myself

Path A: not applicable.

| # | Line I changed (before → after) | AC it breaks | Test that failed |
| --- | --- | --- | --- |
| 1 | n/a (Path A) |  |  |
| 2 | n/a (Path A) |  |  |
| 3 | n/a (Path A) |  |  |

The three failing runs (Path A students leave this block empty):

```

```

---

## 9. What still fails, and what the contract does not say

### 9.1 Checks I am keeping as FAIL or ERROR

The same IDs as `known_fails` in `submission.yml`. Write `none` if the run is clean.

| Check | Why it stays |
| --- | --- |
| none | (confirm after your checker run) |

### 9.2 Outside the contract

The contract says times are integers. It does not say what `can_book` does when one is not —

`600.5`, or the string `"600"`. What does **your** function do, and why is that the right call?

- My function does no type checking. A float such as `660.5` goes through the same comparisons and  

gives a normal True/False answer; a string such as `"660"` raises a `TypeError` on the first
comparison with an integer.

- I think this is the right call: the contract guarantees integers, AC5 says to return `False`  

otherwise but not to raise, and the task says to stay within scope. Extra validation would add a
rule that no AC asks for. In a full system, the layer that reads user input should convert and

check types before calling `can_book`.

### 9.3 A bound that never decides

One of the bounds written in AC1 can never be the *only* reason a request is rejected. Which one,

and why?

- `0 <= start`. `now` is valid (0–1439) and AC1 also requires `start > now`, so `start` is at least 1  

whenever that rule holds. A request with `start < 0` always fails `start > now` as well, so the  
`0 <= start` bound never decides alone. The other bounds can: `start < end` (reversed `(800, 700)`) and  
`end <= 1440` (`(1380, 1441)`) each reject requests that pass every other rule.
## 10. Conclusion (120–180 words)

The overlap condition in my final code is `start < existing_end and existing_start < end`. Two intervals overlap only if each one starts before the other ends. Both comparisons are strict, so for (660, 720) against (600, 660) the check 660 < 660 is false and the booking is allowed, which is what AC4 says about touching endpoints. My v1 passed all my tests and every F check, so I changed nothing. My first checker run failed with an IndentationError in booking.py: copy-paste had added indentation, and 22 checks became ERROR until I restored the file from booking_v1.py. [WRITE ONE SENTENCE FROM YOUR FINAL CHECKER RUN, see below.] I had to decide what happens with non-integer times, because neither the contract nor the assistant covered it. I chose no validation: AC5 says return False, not raise, and extra checks would add a rule that no AC asks for.