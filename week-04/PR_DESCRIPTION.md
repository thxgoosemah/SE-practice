## What I built
A revised use-case diagram (6 use cases, one per story US-01…US-06), a domain class diagram (Student, Room, Booking, BookingStatus) and a sequence diagram for Book room (Student, BookingService, BookingRepository), all in PlantUML in `week-04/models/`, with the AI's original drafts in `models/original/`, rendered images in `models/img/`, the review worksheet, the change log and the checker output.

## AI tools used
Claude Sonnet 5.5 (claude-sonnet-5-5) drafted the three diagrams and, at my request, the revisions and most of the worksheet; @@CRITIC@@ produced the critique in a new chat. Everything is disclosed in `AI_USAGE.md`.

## What the AI got wrong
Use case: Validate booking rules and Send confirmation drawn as goals, and Administrator linked to View room availability (no story). Class: booking workflow on Student, the R2 note on Room instead of Booking, nothing for R4, an enum association with no multiplicities. Sequence: one isAvailable message hid R3 and R2, no branch for an invalid time range (R1), one reply for every failure.

## Time spent
@@TIME@@

## What I would do differently
Run the prompts in a clean chat from the start, review each diagram right after it is drafted, and decide the two open assumptions (touching bookings, blocking a booked room) before drawing anything.
