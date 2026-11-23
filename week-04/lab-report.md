# Week 04 — Lab report: Modeling the System with UML

---

## 1. Setup

| Field | Value |
| --- | --- |
| Name | Zhomartuly Zhanibek |
| Group | CSCI-2208 |
| AI assistant | Claude |
| Exact model | Claude Sonnet 5.5 (claude-sonnet-5-5) |
| Renderer | PlantUML web server |
| Behaviour diagram | sequence |
| Stories used | the reference set from README §3 (US-01 … US-06) |

---

## 2. Prompts as sent

### 2.1 Task 1 — use-case prompt

```text
Using the supplied scenario and approved stories, generate PlantUML for a use-case diagram. Include Student and Administrator outside a named system boundary. Model their goals, show justified associations, and list assumptions. Use include or extend only with a clear reason.
```

### 2.2 Task 2 — class prompt

```text
Create a UML domain class diagram in PlantUML for Smart Campus. Start with Student, Room, and Booking. Add attributes, appropriate operations, and association multiplicities. Add other classes only when requirements justify them. Explain each relationship and list assumptions. Avoid unjustified inheritance or composition.
```

### 2.3 Task 3 — behaviour prompt (3A sequence)

```text
Generate PlantUML for Book room. Use Student, BookingService, and BookingRepository lifelines. Validate the supplied rules, then attempt the reservation. Show a successful confirmation and an unavailable-room alternative using alt. Label messages and replies. Explain new design components and all assumptions.
```

### 2.4 Focused correction prompts (if you sent any)

```text
none
```

### 2.5 Critique prompt

```text
Compare my diagrams with the requirements. Identify missing rules, inconsistent names, and unjustified elements. Cite each issue and propose a specific correction.
```

---

## 3. Task 1 — use-case review

**Assumptions the AI listed:** (1) a student can cancel only their own bookings; (2) an administrator may also view room availability, to decide what to block; (3) rule checking (R1–R3) and the confirmation (R4) are modelled as included use cases so that the rules are visible.

| # | Element | Problem | Rule or story | Fix |
| --- | --- | --- | --- | --- |
| 1 | Administrator → View room availability | The scenario gives availability to students ("Students view room availability"); US-02 is a student story and no administrator story needs it. The AI invented the link in its assumption (2). | Scenario sentence 1; US-02 | Removed the link. Administrator is linked only to Block room (US-04), Unblock room (US-05), Review usage (US-06). |
| 2 | Validate booking rules (included by Book room) | A system step, not a goal anyone sets out to achieve. It traces to no story of its own: R1–R3 are listed inside US-01 as rules of booking. | US-01 (R1, R2, R3) | Removed the use case and its `<<include>>`. R1–R3 are stated in a note on Book room. |
| 3 | Send confirmation (included by Book room) | The confirmation is the outcome of a successful booking ("I get a confirmation when the booking succeeds"), not a goal of a student or administrator. Nothing in the stories asks for it as a separate goal. | R4; US-01 | Removed the use case and its `<<include>>`. R4 is stated in the note on Book room and shown as a message in the sequence diagram. |
| 4 | All associations | The original gave no story ID for any use case, so traceability could not be checked. | US-01 … US-06 | Added a `' US-0x` comment above every association. |

---

## 4. Task 2 — class diagram review

### 4.1 Relationships, read both ways

| Association | Read left → right | Read right → left | Multiplicities |
| --- | --- | --- | --- |
| Student — Booking | One student makes 0..* bookings. | Each booking is made by exactly 1 student. | 1 / 0..* |
| Room — Booking | One room is reserved by 0..* bookings. | Each booking is for exactly 1 room. | 1 / 0..* |

`BookingStatus` is an enum used as the type of `Booking.status`; it is not an association.

### 4.2 Constraints the multiplicities cannot show

- R2: a `note` attached to `Booking` says active bookings for the same room must not overlap, and that touching bookings do not overlap.
- R1 (start in the future, 0 < duration <= 2 hours) is not a multiplicity either: it is in the same note on `Booking`, next to the `start` and `end` attributes.
- R3 is carried by `Room.blocked`.

### 4.3 Assumptions

- A1: Touching bookings are allowed. A booking ending at 12:00 and another starting at 12:00 do not overlap; two bookings overlap only if existing.start < new.end and new.start < existing.end. Reason: the rooms are free at the boundary instant, and R2 forbids overlap, not adjacency.
- A2: Blocking a room keeps existing bookings. R3 says a blocked room "cannot accept a *new* booking"; it says nothing about cancelling old ones, so `Room.block()` only sets `blocked = true`.
- A3: `Booking.confirmationId` is the minimal representation of R4's confirmation. No separate Confirmation class, because R4 gives it no state or behaviour of its own.
- A4: An Administrator class is not added: the scenario needs no administrator state in the domain.

### 4.4 Findings

| # | Element | Problem | Rule or story | Fix |
| --- | --- | --- | --- | --- |
| 1 | Student.bookRoom() and Student.cancelBooking() | Workflow operations on a domain class. The booking workflow (checking R1, R3, R2, then saving) is the job of BookingService in the behaviour diagram, so the same logic was drawn in two places. | US-01, US-03 | Removed both. Cancellation stays as `Booking.cancel()`. |
| 2 | Note with R2 attached to Room | R2 is about pairs of bookings, not about a room; the lab convention puts the R2 note on Booking. | R2 | Moved the note to Booking and added the touching-bookings assumption (A1). |
| 3 | Booking (no confirmation) | Nothing in the model showed R4: a successful booking produces a confirmation. | R4; US-01 | Added `confirmationId : String` to Booking and mentioned it in the note. |
| 4 | Room.isFree(start, end) | A room does not hold its bookings, so it cannot answer this; the sequence diagram has the repository do it with findActiveBookings. | R2 | Removed `isFree`; overlap is decided by the repository query findActiveBookings in the sequence diagram, and R2 is stated in the note on Booking. |
| 5 | Booking --> BookingStatus | An association with no multiplicities at either end, for something that is already shown by the attribute `status : BookingStatus` (check CL3 failed on it). | R2 ("active" bookings) | Removed the line; the enum stays as the attribute type with ACTIVE and CANCELLED. |

---

## 5. Task 3 — behaviour diagram review

**Option chosen and why:** 3A sequence — it shows which component decides each rule and in which order the messages happen, which an activity diagram would not.

**Design components added beyond the domain model:** `BookingService` — receives bookRoom from the student, checks R1, R3 and R2 in that order, creates the booking and returns the confirmation or the rejection; `BookingRepository` — finds a room, finds the active bookings overlapping a time slot and saves a new booking.

| # | Element | Problem | Rule or story | Fix |
| --- | --- | --- | --- | --- |
| 1 | BookingRepository.isAvailable(roomId, start, end) | One message hid both R3 (blocked room) and R2 (overlap) inside the repository, so R3 was nowhere visible and the student could not be told why. | R3, R2 | Replaced it with findRoom + an alt "room blocked" (R3), then findActiveBookings + an alt "unavailable" (R2). |
| 2 | BookingService.checkTimeRange(start, end) (self-message) | The result was never used: no branch for an invalid time range, so R1 could fail with nothing happening. | R1 | Added alt "time range invalid" with a rejection reply before anything else. |
| 3 | Reply "room unavailable" | One reply for every failure; it does not say which rule failed. | R1, R2, R3 | One rejection reply per rule, each naming the rule. |
| 4 | Reply "available / unavailable" from BookingRepository | The repository returned a verdict, so the business decision sat in the data layer. | R2 | The repository now returns data (room, overlapping bookings); BookingService decides. |
| 5 | alt created / else unavailable | The creating branch came first and there was only one decision for three rules. | R1, R2, R3, R4 | Three nested alts, each guarded; save(booking) happens only in the last, innermost created branch. |

---

## 6. AI critique

| # | Issue the AI raised | Element it cited | Verdict | Why |
| --- | --- | --- | --- | --- |
| 1 | bookRoom has no student parameter, so "own bookings" (US-03) cannot be enforced | sequence: `bookRoom(roomId, start, end)` | accept | A booking belongs to exactly one student (Student 1 — 0..* Booking). Changed to `bookRoom(studentId, roomId, start, end)`. |
| 2 | R1 reply "duration not 0 to 2 hours" would accept a duration of 0 | sequence: R1 rejection reply | accept | R1 needs duration > 0 and <= 2 hours. Reworded to "duration not in (0, 2 h]". |
| 3 | R3 is not in the class diagram notes; also add `isBlocked()` | class: `Room.blocked` | accept (note), reject (`isBlocked()`) | The R3 note on Room is cheap and correct. A getter for a private flag is an implementation detail, not a domain operation, so I did not add it. |
| 4 | BookingService and BookingRepository are missing from the class diagram | class.puml vs sequence lifelines | reject | They are design components, not domain concepts; the class review rule is domain classes only (no Service, Repository). They are explained in §5. |
| 5 | `findRoom` is the wrong responsibility for BookingRepository; use a RoomRepository | sequence: `findRoom(roomId)` | reject | The task fixes three lifelines. One repository that persists rooms and bookings is a legitimate simplification. |
| 6 | The sequence PNG has unnamed participants and no message labels | sequence PNG | reject | The source `sequence.puml` declares all three participants and labels every message (checker SQ1 and SQ5 pass on it). The critique read an image, not the source; I re-exported the PNG from the current source and checked that every label shows. |
| 7 | `Student.name` is unjustified; `Room.name` and `Room.capacity` too | class: attributes | accept (Student.name), reject (Room.name, capacity) | No story uses a student's name, so it was removed. A student picks a room from the list by name (US-02) and capacity serves US-06 "plan capacity". |
| 8 | `Booking.overlaps(other)` is never called in the sequence | class: `Booking.overlaps` | accept | The sequence decides R2 through the repository query; the operation was dead. Removed; R2 stays in the note. |
| 9 | Actor-to-use-case arrows should be plain lines | use case: `Student --> UC_Book` etc. | accept | UML associations between an actor and a use case are plain lines; arrowheads suggest a direction that was not intended. |
| 10 | Put US-01 … US-06 in the use-case names | use case names | reject | Names must be goals ("Book room"); the IDs are in the `' US-0x` comments and in §7. |
| 11 | Label the touching-bookings sentence as an assumption; remove "(revised)" from the titles | class note; diagram titles | accept | The sentence is my interpretation of R2 (A1 in §4.3), so the note now says so. "(revised)" is process noise. |
| 12 | Add a service with findAvailableRooms and getUsage for US-02 and US-06 | class vs US-02, US-06 | reject | Only Book room is modelled behaviourally this week; Room and Booking already carry the data those stories read (§7). |

---

## 7. Consistency table

| Requirement / story | Use case | Classes | Behaviour element |
| --- | --- | --- | --- |
| R1 | Book room | Booking (start, end), note on Booking | `checkTimeRange(start, end)` and alt "time range invalid" (R1) |
| R2 | Book room | Booking (start, end, status), note on Booking | `findActiveBookings(roomId, start, end)` and alt "unavailable" (R2) |
| R3 | Block room, Book room | Room (blocked) | `findRoom(roomId)` and alt "room blocked" (R3) |
| R4 | Book room | Booking (confirmationId) | reply "confirmation (R4)" |
| US-01 | Book room | Student, Booking, Room | whole sequence: `bookRoom(roomId, start, end)` |
| US-02 | View room availability | Room (blocked, capacity), Booking (start, end, status) | not modelled in the sequence (only Book room is) |
| US-03 | Cancel booking | Booking (cancel, status) | not modelled in the sequence (only Book room is) |
| US-04 | Block room | Room (blocked, block) | not modelled in the sequence (only Book room is) |
| US-05 | Unblock room | Room (blocked, unblock) | not modelled in the sequence (only Book room is) |
| US-06 | Review usage | Room, Booking (start, end, status) | not modelled in the sequence (only Book room is) |

---

## 8. Change log

| # | Diagram | Before (AI's original) | After (your revision) | Reason |
| --- | --- | --- | --- | --- |
| 1 | use case | 8 use cases, including Validate booking rules and Send confirmation, and Administrator linked to View room availability | 6 use cases, one per story US-01 … US-06, with story-ID comments and a note stating R1–R4 on Book room | Validation and confirmation are system steps (US-01, R4); availability is a student goal (US-02) |
| 2 | class | Student.bookRoom/cancelBooking, Room.isFree, R2 note on Room, no confirmation, Booking --> BookingStatus | Those operations removed, R2 note on Booking, `confirmationId` added, dangling association removed | Workflow belongs to BookingService; R2 is about bookings; R4; no multiplicity on the enum line |
| 3 | sequence | One isAvailable call, one alt created/unavailable, R1 and R3 not visible | Three nested guarded alts (R1, R3, R2), repository returns data, save only in the last branch | R1, R2, R3, R4; nothing saved on a failure |
| 4 | use case | Actor-to-use-case associations drawn as arrows (`-->`) | Plain lines (`--`) | Critique 9: an association has no direction here |
| 5 | class | `Student.name`, `Booking.overlaps(other)`, no R3 note, label "is reserved by", note not marked as assumption | Removed `Student.name` and `overlaps`; added R3 note on Room, label "has", "Assumption A1" in the note | Critique 3, 7, 8, 11; no story uses the student's name; R2 is decided by the query |
| 6 | sequence | `bookRoom(roomId, start, end)`; R1 reply "duration not 0 to 2 hours"; no creation step | `bookRoom(studentId, roomId, start, end)`; "duration not in (0, 2 h]"; note: new Booking ACTIVE with confirmationId | Critique 1, 2; US-03 own bookings; R1; R4 |

---

## 9. Checker output

```text
Week 04 structural check - shape only, never quality

UC1  PASS  Student and Administrator declared
UC2  PASS  named system boundary: "Smart Campus Room Booking"
UC3  PASS  all actors declared outside the boundary
UC4  PASS  all scenario goals present (6 use cases)
UC5  PASS  no actor is associated with a confirmation use case
UC6  PASS  actor responsibilities match the scenario
UC7  PASS  use cases are goals, not screens or components
UC8  PASS  every include / extend / generalization carries a ' why: comment (or there are none)
UC9  PASS  revised diagram differs from the AI's original
CL1  PASS  Student, Room and Booking present
CL2  PASS  Booking is associated with Student and with Room
CL3  PASS  every association has multiplicities at both ends
CL4  PASS  1 student / 1 room per booking, 0..* bookings per student and per room
CL5  PASS  every inheritance / composition / aggregation carries a ' why: comment (or there are none)
CL6  PASS  only domain concepts in the class diagram
CL7  PASS  attributes needed by R1-R3 are present
CL8  PASS  a note states R2 (no overlapping active bookings)
SQ1  PASS  Student, BookingService and BookingRepository lifelines present
SQ2  PASS  alt block with a guard on every branch (6 branches)
SQ3  PASS  validation happens before creation
SQ4  PASS  nothing is saved on a failure branch
SQ5  PASS  every message is labelled
SQ6  PASS  R1 (time range) is visible - checked or stated as a precondition
SQ7  PASS  R3 (blocked room) is visible
FI1  PASS  the AI's original output is kept for every diagram
FI2  PASS  a rendered image for every diagram
LR1  PASS  §1 setup filled (tool and model recorded)
LR2  PASS  5 prompts pasted in §2
LR3  PASS  2 use-case findings in §3
LR4  PASS  §4 relationships read both ways, 4 assumption(s) declared
LR5  PASS  5 behaviour-diagram findings in §5
LR6  PASS  12 critique issues with a verdict
LR7  PASS  6 change-log rows covering all three diagrams
CS1  PASS  6 approved stories
CS2  PASS  §7 traces R1-R4 into the diagrams
CS3  PASS  every use case traces to an approved story
CS4  PASS  every lifeline is a domain class or an explained design component

SUMMARY pass=37 fail=0 error=0
A FAIL you report and explain in lab-report.md §9 costs you nothing. One you hide costs the criterion.
```

**FAILs I am keeping, and why:** none (no FAIL)

---

## 10. Conclusion (120–180 words)

The class diagram was the draft that carried the most wrong design: it put booking workflow on Student (bookRoom, cancelBooking), attached the R2 note to Room although R2 compares pairs of bookings, and left R4 with no trace in the model. In the sequence diagram the worst error was the single isAvailable message: it hid R3 and R2 inside the repository, so a blocked room was indistinguishable from an overlap, and the student could never learn which rule failed. Had nobody reviewed it, that merged check would have reached the code as one boolean and the blocked-room rule would have been untested. In the use-case diagram, Validate booking rules and Send confirmation were system steps drawn as goals, and Administrator had a link to View room availability that no story gives it. The critique in §6 is another claim, not a verdict. It found things I missed: bookRoom had no student parameter, so "own bookings" (US-03) could not be enforced, and the R1 reply "duration not 0 to 2 hours" read as accepting 0. It also claimed things that were false or wrong for this lab: that the sequence image had no labels (the source has them), and that Service and Repository classes belong in a domain diagram. I accepted 7 of 12 points fully or in part and rejected the rest with a reason.
