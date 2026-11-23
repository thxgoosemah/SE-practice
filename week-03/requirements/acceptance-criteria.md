# Acceptance criteria — three selected stories
# WEEK 03 PR CHECKLINE


Assumptions first, then the criteria. Each block names the story it belongs to. 3 to 5 criteria per
story, every one in Given / When / Then form, and every set covers a validation or error case — not
three happy paths.

---

## Assumptions

- **Overlap:** a booking that ends exactly when another begins does **not** overlap under R3 —
  back-to-back bookings for the same room are allowed.
- **Duration:** a booking of exactly two hours **is** allowed under R2 — the two-hour maximum is
  inclusive, not a strict upper bound.
- Only the student who created a booking may cancel it; there is no separate approval step.
- All time comparisons use the system's current time; "future" (R1) means strictly later than now.

---

## US-02 — Book room

### AC-01
- **Given** a room is free for the requested time slot, the slot starts in the future, and the duration is at most two hours
- **When** the Student requests the booking
- **Then** the system creates the booking and marks the room as reserved for that slot

### AC-02
- **Given** the requested time slot overlaps an existing booking for the same room (R3)
- **When** the Student requests the booking
- **Then** the system rejects the request with an overlap error and no booking is created

### AC-03
- **Given** the requested start time is not in the future (R1)
- **When** the Student requests the booking
- **Then** the system rejects the request with an invalid-time error

### AC-04
- **Given** the requested duration is more than two hours (R2)
- **When** the Student requests the booking
- **Then** the system rejects the request with a duration error

### AC-05
- **Given** the requested room is currently blocked (R4)
- **When** the Student requests the booking
- **Then** the system rejects the request with a room-unavailable error

---

## US-03 — Cancel booking

### AC-06
- **Given** the Student has an existing future booking
- **When** the Student cancels it
- **Then** the system releases the booking and the room becomes available for that slot again

### AC-07
- **Given** a booking exists that was made by a different student
- **When** the Student attempts to cancel it
- **Then** the system rejects the request with an authorization error and the booking is not cancelled

### AC-08
- **Given** the referenced booking ID does not exist
- **When** the Student attempts to cancel it
- **Then** the system rejects the request with a not-found error

---

## US-04 — Block or unblock room

### AC-09
- **Given** a room is not currently blocked
- **When** the Administrator blocks it
- **Then** the room's status becomes blocked and it can no longer be booked (R4)

### AC-10
- **Given** a room is currently blocked
- **When** the Administrator unblocks it
- **Then** the room's status becomes available and it can be booked again

### AC-11
- **Given** a room is already blocked
- **When** the Administrator blocks it again
- **Then** the system leaves the room's status unchanged and returns no error

### AC-12
- **Given** a room is not currently blocked
- **When** the Administrator attempts to unblock it
- **Then** the system rejects the request with an invalid-state error, since it was never blocked
