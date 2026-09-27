# Lab report — Practice #03, Requirements Engineering with AI

Fill in every section. **Do not delete or renumber the headings** — the README points at them and a
missing heading reads as a missing section.

Name: Zhanibek Zhomartuly
Student ID: 24b031040
GitHub username: thxgoosemah

---

## 1. Setup

| | |
| --- | --- |
| AI assistant (tool) | Claude |
| Exact model name and version | Claude Sonnet 5 (model id `claude-sonnet-5`) |
| Date of the session | 27.09.2026 |
| Diagram renderer used | plantuml.com/plantuml |

One tool and one model for all three prompts. If you switched, say why here — it changes what your
findings mean.

Same tool and same model (Claude Sonnet 5) for all three prompts, each in its own fresh chat, as
required.

---

## 2. Original AI output — user stories (Part 1)

### US-01
**Story:** As a Student, I want to view available study rooms and their time slots, so that I can choose a suitable room for studying.
**Priority:** High
**Assumption:** Room availability is determined by existing bookings and room blocking status.

### US-02
**Story:** As a Student, I want to book an available study room for a future time slot, so that I can reserve a place for individual or group study.
**Priority:** High
**Assumption:** Students can book rooms for themselves or their study groups.

### US-03
**Story:** As a Student, I want to cancel a booking I made, so that I can release a room I no longer need.
**Priority:** Medium
**Assumption:** Students can cancel only their own bookings.

### US-04
**Story:** As an Administrator, I want to block a study room, so that students cannot book it while it is unavailable.
**Priority:** High
**Assumption:** An administrator can block a room that is not currently available for use.

### US-05
**Story:** As an Administrator, I want to unblock a study room, so that students can book it again when it becomes available.
**Priority:** Medium
**Assumption:** Only an administrator can unblock a room.

### US-06
**Story:** As an Administrator, I want to review room usage over a selected period, so that I can understand how the study rooms are being used.
**Priority:** Medium
**Assumption:** Usage information can be summarized over a specified period.

### US-07
**Story:** As a Student, I want to receive confirmation when my booking or cancellation is processed, so that I know whether my request was successful.
**Priority:** High
**Assumption:** The system sends a confirmation after a successful booking or cancellation.

### US-08
**Story:** As an Administrator, I want to receive notifications about room bookings, so that I can monitor student activity in the library.
**Priority:** Low
**Assumption:** Administrators can receive notifications when students make bookings.

## 3. Story review (Part 2)

| Story (as generated) | What I did | Why | Final ID |
| --- | --- | --- | --- |
| US-01 — view available rooms and time slots | Kept unchanged | Names a real stakeholder (Student), describes one valuable outcome, testable, small enough for one iteration. | US-01 |
| US-02 — book an available room for a future slot | Kept unchanged | Same reasons as US-01; matches UC-02 directly, no invented detail beyond the scenario. | US-02 |
| US-03 — cancel a booking | Kept unchanged | Maps directly to UC-03; the assumption ("students can cancel only their own bookings") stays inside the scenario. | US-03 |
| US-04 — block a study room | Kept unchanged | Maps directly to UC-04 (block direction); real stakeholder, testable. | US-04 |
| US-05 — unblock a study room | Kept unchanged | Maps to UC-04 (unblock direction); kept as a separate story rather than merging with US-04 because each direction has its own precondition and is independently testable. | US-05 |
| US-06 — review room usage over a period | Kept unchanged | Maps directly to UC-05; Administrator is a real stakeholder, outcome is valuable and testable. | US-06 |
| US-07 — receive confirmation of booking/cancellation | Kept unchanged | Maps directly to UC-06; this is the one use case that has no other natural "owner" story, so it stays. | US-07 |
| US-08 — Administrator receives notifications about bookings to monitor student activity | **Deleted** | This is a seventh function that does not correspond to any of the six fixed use cases (UC-01…UC-06). "Monitoring student activity in real time" is a different, broader capability than UC-05 "Review usage" (which is a look-back report over a period, not live notifications) and than UC-06 "Send confirmation" (which is a message to the Student, not to the Administrator). It is not on the literal out-of-scope keyword list, but it widens the scenario the same way an out-of-scope item would — a case the checker's keyword search cannot catch and a human review has to. | — (removed) |

**Did the assistant invent anything outside the scenario?**
Yes — US-08. It quietly added a "live activity monitoring / notifications to the Administrator"
capability that isn't one of the six fixed use cases and isn't required by any business rule in
section 1. It doesn't trip the out-of-scope keyword checker (it never says "push notification" or
"reminder" — those are reserved for the student-facing case in UC-06), which is exactly why this had
to be caught by reading the story, not by running a script. I checked every other story against the
out-of-scope list (payments, QR/check-in, maintenance, SMS/push/reminder beyond UC-06,
registration/auth, waiting lists, screens/DB) and found nothing else.

**How many stories did you end with, and why that number?**
7 (US-01…US-07). I didn't force it down to 6 or merge anything further, because each remaining story
maps to exactly one of the six use cases and stands on its own as an independently testable
increment — merging any two of them (e.g. block/unblock) would have hidden two different
preconditions behind one story. Removing US-08 was the only change needed to get back inside the
scenario's boundaries.

## 4. Original AI output — acceptance criteria (Part 3)

Assumptions (including the two required decisions)
A1 (R3 boundary — required decision): A booking that ends exactly when another begins is not an overlap. Back-to-back bookings (e.g., 10:00–11:00 and 11:00–12:00) are allowed.
A2 (R2 boundary — required decision): A duration of exactly two hours is allowed. The rule is "duration ≤ 2 hours," not "< 2 hours."
A3: "Future" in R1 means strictly later than the current system time at the moment of booking; a start time equal to "now" is rejected.
A4: Only the student who made a booking can cancel it (no staff-cancels-for-student flow is in scope, since that's not one of the six listed use cases).
A5: UC-06 (Send confirmation) is triggered automatically as a consequence of UC-02 (Book) and UC-03 (Cancel) succeeding — it is not a separately initiated action by either actor.
A6: UC-04 (Block/unblock) does not retroactively cancel existing bookings already made before the block; it only prevents new bookings while blocked. (No auto-cancel rule was given, so none is invented.)
A7: UC-05 (Review usage) is read-only reporting over a period the Administrator specifies; it does not modify any booking or room state.
A8: "Room" and "time slot" are treated as plain data (room identifier, start time, end time) — no assumptions about UI, database, or hardware are made, per the out-of-scope list.
User Stories & Acceptance Criteria
UC-01 — View availability

Story: As a Student, I want to view room availability so that I can find a free room for a chosen time.

Given rooms exist with a mix of free and booked time slots, When a Student requests availability for a given day, Then the system shows, for each room, the slots that are free and the slots that are already booked.
Given a room has been blocked by an Administrator, When a Student views availability, Then that room is shown as unavailable for the entire blocked period.
Given a Student requests availability for a date with no bookings or blocks at all, When the request is made, Then the system shows every room as fully free for that date.
Given a Student requests availability without specifying any date or room, When the request is submitted, Then the system rejects the request and asks for at least a date to check.
UC-02 — Book room

Story: As a Student, I want to book a free room for a time slot so that I can study there.

Given a room is free for the requested slot, When a Student books that room with a start time in the future and a duration of two hours or less, Then the booking is created and confirmed (triggers UC-06).
Given a Student submits a start time that is not in the future (equal to or before "now"), When the booking is attempted, Then the system rejects the booking with a validation error (R1).
Given a Student requests a duration longer than two hours, When the booking is attempted, Then the system rejects the booking with a validation error (R2).
Given the requested room already has a booking that overlaps the requested slot (not merely back-to-back), When the booking is attempted, Then the system rejects the booking as a conflict (R3).
Given the requested room is currently blocked, When a Student attempts to book it, Then the system rejects the booking because the room is unavailable (R4).
UC-03 — Cancel booking

Story: As a Student, I want to cancel my booking so that I free up the room for others.

Given a Student has an existing future booking, When the Student cancels it, Then the booking is removed and the room becomes free for that slot again, and a cancellation confirmation is sent (triggers UC-06).
Given a Student tries to cancel a booking that does not belong to them, When the cancellation is attempted, Then the system rejects the request as not permitted.
Given a Student tries to cancel a booking that has already started or already ended, When the cancellation is attempted, Then the system rejects the request as the booking is no longer cancellable.
Given a Student tries to cancel a booking ID that does not exist, When the cancellation is attempted, Then the system rejects the request with a "booking not found" error.
UC-04 — Block or unblock room

Story: As an Administrator, I want to block or unblock a room so that unusable rooms are kept out of booking and restored when ready.

Given a room is currently free/unblocked, When an Administrator blocks it, Then the room is marked blocked and no new bookings can be made against it (R4) until it's unblocked.
Given a room is currently blocked, When an Administrator unblocks it, Then the room becomes bookable again for future slots.
Given a room is already blocked, When an Administrator attempts to block it again, Then the system rejects the action as redundant/invalid (already in that state).
Given a room is already unblocked, When an Administrator attempts to unblock it again, Then the system rejects the action as redundant/invalid (already in that state).
UC-05 — Review usage

Story: As an Administrator, I want to review room usage over a period so that I can understand how rooms are being utilized.

Given bookings and cancellations exist within a chosen period, When an Administrator requests a usage review for that period, Then the system returns a summary of bookings (and cancellations) per room for that period.
Given a chosen period has no bookings at all, When the Administrator requests the review, Then the system returns an empty/zero-usage result rather than an error.
Given an Administrator requests a review with an end date earlier than the start date, When the request is submitted, Then the system rejects the request as an invalid period.
Given a Student (not an Administrator) attempts to request a usage review, When the request is submitted, Then the system rejects it as not permitted for that role.
UC-06 — Send confirmation

Story: As a Student, I want to receive confirmation of my booking or cancellation so that I know the action succeeded.

Given UC-02 (Book) completes successfully, When the booking is created, Then the system sends a booking confirmation to the Student.
Given UC-03 (Cancel) completes successfully, When the booking is cancelled, Then the system sends a cancellation confirmation to the Student.
Given a booking attempt fails validation (R1, R2, R3, or R4), When the failure occurs, Then no confirmation is sent, since no successful action occurred.
Given a confirmation cannot be delivered (e.g., delivery failure), When this occurs, Then the underlying booking/cancellation remains valid — confirmation delivery failure does not undo the action.

---

## 5. Criteria review (Part 3)

| Criterion (as generated) | Problem | What I changed it to | Final ID |
| --- | --- | --- | --- |
| Book room, AC-01: "...the booking is created and confirmed (triggers UC-06)." | Bundles two use cases' effects into one Then-clause — confirmation is UC-06's own outcome, not Book room's. | Dropped "and confirmed"; kept only the booking-creation effect. | AC-01 |
| Cancel booking, AC-06: "...and a cancellation confirmation is sent (triggers UC-06)." | Same issue. | Dropped the confirmation clause. | AC-06 |
| Cancel booking: "...has already started or already ended... no longer cancellable." | Not one of the four fixed business rules (R1-R4) and not needed given R1 already scopes bookings to future start times. | Dropped — kept the 3 criteria that map cleanly to ownership, existence and the happy path instead of a fourth, rule-less state check. | — (removed) |
| Block/unblock, "re-block an already-blocked room... rejects... redundant/invalid" | Raw output treated this as an error with no stated business rule requiring it; nothing in R1-R4 says a repeat block must fail. | Changed to an idempotent no-op (status unchanged, no error) — the less presumptive choice when the scenario is silent. | AC-11 |

**Note on the raw output's quality this time:** unlike a typical run, this generation already covered
R1-R4 for Book room and already included the authorization case for Cancel booking — there was
nothing missing to add there. The real review work was narrower: separating confirmation out of
Book/Cancel's Then-clauses, dropping one rule-less criterion, and reconsidering one inconsistent
"reject vs. no-op" decision.

**Additional finding — unsolicited scope creep:** the raw response to Prompt 2 also appended an
unrequested `submission.yml` suggestion (fields like `actors`, `use_cases`, `out_of_scope_respected`)
that doesn't match this course's fixed schema. It was discarded entirely and never used.

---

## 6. Original AI output — use-case diagram (Part 4)

@startuml SmartCampus_StudyRoomBooking
left to right direction
skinparam packageStyle rectangle

actor Student
actor Administrator

rectangle "Smart Campus - Study Room Booking" {
  usecase "View availability"        as UC1
  usecase "Book room"                as UC2
  usecase "Cancel booking"           as UC3
  usecase "Block or unblock room"    as UC4
  usecase "Review usage"             as UC5
  usecase "Send confirmation"        as UC6
}

Student       --> UC1
Student       --> UC2
Student       --> UC3

Administrator --> UC4
Administrator --> UC5

UC2 .> UC6 : <<include>>
UC3 .> UC6 : <<include>>
@enduml

Reasoning behind the associations, kept to only what the scenario supports:

Student links to UC-01, UC-02, UC-03 — these are the only actions a student directly initiates.
Administrator links to UC-04 and UC-05 — the only actions staff directly initiate.
UC-06 (Send confirmation) has no direct actor line. The notes say "the system confirms a booking or a cancellation," which reads as a system-triggered consequence, not something either actor initiates on its own. I modeled it as <<include>>d by UC-02 and UC-03, since both explicitly produce a confirmation per the spec.
No <<extend>> was used — nothing in the six use cases describes an optional, conditional branch off another use case; the two include relationships were the only ones the text clearly justifies.
I did not include UC-01 into UC-02 (i.e., did not model "Book room" as including "View availability"), since the scenario never states that booking mechanically reuses the availability-viewing use case — that would be inventing structure not given.
No screens, databases, or internal classes appear, per the out-of-scope list.

---

## 7. Diagram review (Part 4)

The raw diagram had no actor–use-case association that was actually wrong: Student was already
correctly wired only to UC-01/02/03, Administrator only to UC-04/05, and UC-06 already had no
direct actor line, modeled instead as `<<include>>`d by UC-02 and UC-03. There was nothing to
correct on the actor-association front — reported honestly rather than inventing a fix that
didn't happen.

What I did change:
| Element | Problem | What I changed |
| --- | --- | --- |
| `UC2 .> UC6 : <<include>>` / `UC3 .> UC6` | `.>` is not valid PlantUML dashed-arrow syntax — the correct token is `..>`. As written it would fail or render incorrectly in most renderers. | Changed to `..>` for both include relations. |
| `usecase "..." as UC1..UC6` | Aliases didn't match the course's fixed `UC-nn` ID scheme used everywhere else (stories, criteria, traceability). | Renamed aliases to `UC01…UC06` so the diagram's internal IDs line up with the rest of the artifacts. |
| `skinparam packageStyle rectangle`, named `@startuml SmartCampus_StudyRoomBooking` | Cosmetic only, no functional effect. | Removed / simplified — not a correctness issue, just cleanup. |

**Associations.** No actor–use-case link needed removing — the assistant got this right the first
time. (This is itself worth stating explicitly, per the FAQ: "a defended disagreement/finding is
worth more than a silent edit to make the checker green" — the honest finding here is *no wrong
association existed*, not that one was invented and then fixed.)

**Did any screen, database or internal component appear as a use case or an actor?**
No — the raw output never introduced any.

---

## 8. Traceability (Part 5)

Summarise what the table in `requirements/traceability.md` shows:

- Use cases with **no story** behind them: none — all six use cases have at least one story.
- Stories with **no use case** they belong to: none — every one of US-01…US-07 is listed in the table.
- Criteria that test **no rule** from section 1: none — every acceptance criterion for Book room ties
  to one of R1–R4, and the Cancel/Block criteria test ownership and state transitions that follow
  directly from the use case notes.

**What does the largest gap tell you about the generated requirements?**
The largest gap is that UC-06 "Send confirmation" has no dedicated acceptance criteria and no actor of
its own anywhere in the artifacts — it only ever shows up as the observable "and confirmed" half of
AC-01 (booking) and AC-06 (cancellation). That tells me it isn't really an independent function the
way the other five are: it's a guaranteed side effect of two other use cases succeeding, which is
exactly why the diagram models it with `<<include>>` rather than a direct actor association. If I were
implementing this, I would not build a standalone "send confirmation" feature — I'd build it as a
step inside the booking and cancellation flows.

---

## 9. Checker runs

Paste the **real terminal output** of both runs. A table with nothing behind it does not count.

First run (before fixes):

$ python tests/check_requirements.py
FAIL   US-1  user-stories.md         2 TODO placeholder(s) left in the file
PASS   US-2  user-stories.md         7 stories, IDs US-01…US-07
PASS   US-3  user-stories.md         every story has the required sentence shape
PASS   US-4  user-stories.md         every story has a priority
PASS   US-5  user-stories.md         every story declares an assumption
PASS   US-6  user-stories.md         only Student and Administrator appear as roles
PASS   US-7  user-stories.md         nothing from the out-of-scope list appears
PASS   AC-1  acceptance-criteria.md  no placeholders left
PASS   AC-2  acceptance-criteria.md  three sections, all naming real stories: US-02, US-03, US-04
PASS   AC-3  acceptance-criteria.md  every section has 3 to 5 uniquely numbered criteria
PASS   AC-4  acceptance-criteria.md  all 12 criteria are complete Given/When/Then
PASS   AC-5  acceptance-criteria.md  every section covers an invalid or boundary case
PASS   AC-6  acceptance-criteria.md  4 assumptions listed before the criteria
PASS   AC-7  acceptance-criteria.md  both open questions are settled in the assumptions
PASS   PU-1  use-cases.puml          valid PlantUML block, no placeholders
PASS   PU-2  use-cases.puml          exactly two actors: Student, Administrator
PASS   PU-3  use-cases.puml          all six use cases present
PASS   PU-4  use-cases.puml          system boundary present
PASS   PU-5  use-cases.puml          no screens, databases or internal components
PASS   PU-6  use-cases.puml          no unjustified actor associations found
PASS   TR-1  traceability.md         all six use cases have a row
PASS   TR-2  traceability.md         every ID in the table resolves
PASS   TR-3  traceability.md         every story appears in the table
------------------------------------------------------------------------
22 PASS · 1 FAIL · 0 ERROR   (23 checks)

$ python tests/validate_submission.py
ERROR  submission.yml cannot be parsed — line 54: expected `key:` or `key: value`, got '"US-08 invented..."'
       Keep the shape the template ships with: two-space indents, no tabs.

Second run (after fixes, final):

$ python tests/check_requirements.py
[... all 23 lines PASS ...]
23 PASS · 0 FAIL · 0 ERROR   (23 checks)
Shape is clean. This says nothing about whether the requirements are good.

$ python tests/validate_submission.py
21 PASS · 0 FAIL · 0 ERROR · 1 note
NOTE   checker   you are claiming a clean run — it will be re-run at your commit, so make sure it is true
Shape is fine. This says nothing about whether the work is good.

| | PASS | FAIL | ERROR |
| --- | --- | --- | --- |
| `check_requirements.py` | 23 | 0 | 0 |

Commit these numbers were produced at (`git rev-parse --short HEAD`): `<paste your real hash here>`

**Every FAIL, one line each: what it is and what you decided to do about it.** A FAIL you report and
explain costs you nothing.

- `US-1` (`user-stories.md`): the file still had the template's own instructional line —
  "Delete the TODO lines as you fill them in — the checker treats a leftover TODO as unfinished
  work." — which contains the literal word "TODO" twice and tripped the checker's placeholder
  regex. It was not an unfinished story, just leftover boilerplate at the top of the file that I
  forgot to remove after filling in US-01…US-07. Decision: deleted the line and re-ran; the check
  now passes (23/23).
- `submission.yml` initially failed to parse (`ERROR`, not `FAIL`): `review_findings` was written as
  a single bare string at column 0 instead of a `- "item"` list with three or more entries.
  Decision: reformatted it as a proper YAML list with three findings, each naming a real ID
  (`US-08`, `UC-06`, `UC-01`/`UC-05`), and re-ran; it now validates clean.

**Did you run the checks by hand instead of with Python?** No — both were run with the shipped
Python scripts, first against the original files, then again after the two fixes above. Both
terminal outputs above are pasted as they came out, unedited.

---

## 10. Conclusion (150–200 words)

The single most interesting thing about this run was that the AI's raw outputs came out cleaner
than a typical generation: the diagram had no wrong actor association at all — Student was already
wired only to View availability/Book/Cancel, Administrator only to Block-unblock/Review usage, and
Send confirmation already had no direct actor line, modeled as an `<<include>>` off Book room and
Cancel booking. The acceptance criteria for Book room already covered all four business rules, and
Cancel booking already had its authorization case. So the review work here was narrower than usual:
catching one invalid PlantUML token (`.>` instead of the valid `..>`), aligning use-case aliases to
the `UC-nn` convention, removing one scope-creep story (US-08, an Administrator live-monitoring
feature matching none of the six fixed use cases), pulling the "confirmation sent" effect out of
Book/Cancel's Then-clauses since that belongs to UC-06 on its own, dropping one rule-less Cancel
criterion, and reconsidering an inconsistent reject-vs-no-op decision for re-blocking an
already-blocked room.

What the assistant got right, and would have taken longer by hand, was the mechanical structure and,
this time, most of the substance too — freeing my time for a genuinely careful line-by-line check
instead of first-pass cleanup.

If I handed this off to someone else, I'd settle US-04/US-05 (block/unblock) first: the scenario
never says what happens to existing future bookings when a room is blocked, and nothing in the
artifacts answers it — an implementer would have to guess.
