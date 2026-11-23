import type { CheckInput, CheckResult } from "../types";
import { getBookingIssue } from "../booking";
import { fmtTime } from "./time";

/**
 * Pure availability check implementing AC1–AC5.
 * Never mutates the room's bookings (AC5).
 */
export function checkAvailability(input: CheckInput): CheckResult {
  const { room, currentTimeMin, startMin, endMin } = input;
  const issue = getBookingIssue({
    start: startMin,
    end: endMin,
    now: currentTimeMin,
    blocked: room.blocked,
    bookings: room.bookings,
  });

  // Keep the original UI messages; booking.ts owns the decision rules.
  if (issue?.kind === "interval") {
    return {
      decision: "invalid",
      reason:
        "Enter a valid interval: 0 ≤ start < end ≤ 1440 minutes (00:00–24:00).",
    };
  }
  if (issue?.kind === "past") {
    return {
      decision: "invalid",
      reason: `Start time must be after the current time (${fmtTime(currentTimeMin)}).`,
    };
  }

  // AC2: reject bookings longer than 120 minutes.
  if (issue?.kind === "duration") {
    return {
      decision: "unavailable",
      reason: `Requested length is ${endMin - startMin} min, but the maximum is 120 min.`,
    };
  }

  // AC3: reject when the room is blocked.
  if (issue?.kind === "blocked") {
    return {
      decision: "unavailable",
      reason: "This room is blocked and cannot be booked.",
    };
  }

  if (issue?.kind === "overlap") {
    const { conflict } = issue;
    return {
      decision: "unavailable",
      reason: `Overlaps an existing booking (${fmtTime(conflict.start)}–${fmtTime(conflict.end)}). Touching endpoints are allowed.`,
      conflict,
    };
  }

  return {
    decision: "available",
    reason: `Interval ${fmtTime(startMin)}–${fmtTime(endMin)} is available (${endMin - startMin} min).`,
  };
}
