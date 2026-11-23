export type Booking = { start: number; end: number };

type BookingInput = {
  start: number;
  end: number;
  now: number;
  blocked: boolean;
  bookings: readonly Booking[];
};

type BookingIssue =
  | { kind: "interval" | "past" | "duration" | "blocked" }
  | { kind: "overlap"; conflict: Booking };

// Shared pure availability validation implementing AC1–AC5.
export function getBookingIssue({
  start, end, now, blocked, bookings,
}: BookingInput): BookingIssue | null {
  if (
    !Number.isFinite(start) ||
    !Number.isFinite(end) ||
    !Number.isInteger(start) ||
    !Number.isInteger(end) ||
    !(start >= 0 && end <= 1440 && start < end)
  ) {
    return { kind: "interval" };
  }
  if (start <= now) return { kind: "past" };
  if (end - start > 120) return { kind: "duration" };
  if (blocked) return { kind: "blocked" };

  const conflict = bookings.find((b) => start < b.end && end > b.start);
  if (conflict) return { kind: "overlap", conflict };
  return null;
}

export function canBook({ start, end, now, blocked, bookings }: {
  start: number;
  end: number;
  now: number;
  blocked: boolean;
  bookings: readonly Booking[];
}): boolean {
  return getBookingIssue({ start, end, now, blocked, bookings }) === null;
}
