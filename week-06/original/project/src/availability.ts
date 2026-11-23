import type { Booking, CheckResult, IntervalInput, Room } from "@/types";
import { MAX_BOOKING_MINUTES, MINUTES_PER_DAY } from "@/types";

export function minutesToLabel(min: number): string {
  const m = ((min % MINUTES_PER_DAY) + MINUTES_PER_DAY) % MINUTES_PER_DAY;
  const h = Math.floor(m / 60);
  const mm = m % 60;
  return `${String(h).padStart(2, "0")}:${String(mm).padStart(2, "0")}`;
}

export function labelToMinutes(label: string): number | null {
  const match = label.trim().match(/^(\d{1,2}):(\d{2})$/);
  if (!match) return null;
  const h = Number(match[1]);
  const mm = Number(match[2]);
  if (h < 0 || h > 23 || mm < 0 || mm > 59) return null;
  return h * 60 + mm;
}

export function checkAvailability(
  room: Room | undefined,
  bookings: Booking[],
  input: IntervalInput,
  nowMinutes: number
): CheckResult {
  const reasons: string[] = [];
  const { start, end } = input;

  if (!room) {
    return { decision: "Unavailable", reasons: ["No room selected."] };
  }

  // AC1: valid interval bounds and start must be after current time.
  if (Number.isNaN(start) || Number.isNaN(end)) {
    reasons.push("Start and end times are required.");
  } else {
    if (start < 0 || end < 0) {
      reasons.push("Times cannot be earlier than 00:00.");
    }
    if (!(start < end)) {
      reasons.push("Start time must be earlier than the end time.");
    }
    if (end > MINUTES_PER_DAY) {
      reasons.push("End time cannot go past 24:00.");
    }
    if (start <= nowMinutes) {
      reasons.push(
        `Start time must be after the current time (${minutesToLabel(nowMinutes)}).`
      );
    }
  }

  // AC2: max booking length.
  const duration = end - start;
  if (!Number.isNaN(duration) && duration > MAX_BOOKING_MINUTES) {
    reasons.push(
      `Booking is ${duration} minutes; maximum allowed is ${MAX_BOOKING_MINUTES} minutes.`
    );
  }

  // AC3: room blocked.
  if (room.blocked) {
    reasons.push(
      `This room is blocked: ${room.blockedReason ?? "unavailable for booking."}`
    );
  }

  // AC4: overlap with existing bookings (touching endpoints allowed).
  if (Number.isNaN(start) || Number.isNaN(end) || !(start < end)) {
    // skip overlap check when the interval itself is invalid
  } else {
    const overlapping = bookings.filter(
      (b) => b.roomId === room.id && start < b.end && b.start < end
    );
    for (const b of overlapping) {
      reasons.push(
        `Overlaps "${b.title}" (${minutesToLabel(b.start)}–${minutesToLabel(b.end)}).`
      );
    }
  }

  return {
    decision: reasons.length === 0 ? "Available" : "Unavailable",
    reasons,
  };
}
