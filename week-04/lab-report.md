# Week 04 — Lab report: Modeling the System with UML

---

## 1. Setup

| Field | Value |
| --- | --- |
| Name | @@NAME@@ |
| Group | @@GROUP@@ |
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
| 4 | Room.isFree(start, end) | A room does not hold its bookings, so it cannot answer this; the sequence diagram has the repository do it with findActiveBookings. | R2 | Removed `isFree`; overlap is `Booking.overlaps(other)` plus the repository query. |
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
| 1 | <issue> | <element> | <accept / reject> | <your reason> |
| 2 | <issue> | <element> | <accept / reject> | <your reason> |
| 3 | <issue> | <element> | <accept / reject> | <your reason> |

---

## 7. Consistency table

| Requirement / story | Use case | Classes | Behaviour element |
| --- | --- | --- | --- |
| R1 | Book room | Booking (start, end), note on Booking | `checkTimeRange(start, end)` and alt "time range invalid" (R1) |
| R2 | Book room | Booking (overlaps, status), note on Booking | `findActiveBookings(roomId, start, end)` and alt "unavailable" (R2) |
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

---

## 9. Checker output

```text
@@CHECKER_OUTPUT@@
```

**FAILs I am keeping, and why:** @@KEPT_FAILS@@

---

## 10. Conclusion (120–180 words)

The class diagram was the draft that carried the most wrong design: it put booking workflow on Student (bookRoom, cancelBooking), attached the R2 note to Room although R2 compares pairs of bookings, and left R4 with no trace in the model. In the sequence diagram the worst error was the single isAvailable message: it hid R3 and R2 inside the repository, so a blocked room was indistinguishable from an overlap, and the student could never learn which rule failed. Had nobody reviewed it, that merged check would have reached the code as one boolean and the blocked-room rule would have been untested. In the use-case diagram, Validate booking rules and Send confirmation were system steps drawn as goals, and Administrator had a link to View room availability that no story gives it. The critique in §6 is another claim, not a verdict: @@CONCLUSION_CRITIQUE@@
