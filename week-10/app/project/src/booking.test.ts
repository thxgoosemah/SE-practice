import { describe, expect, it } from "vitest";
import { canBook, type Booking } from "./booking";

it("BUG-A: allows a 30-minute request touching two bookings at both endpoints (AC4)", () => {
  const bookings: Booking[] = [
    { start: 600, end: 660 },
    { start: 690, end: 750 },
  ];

  expect(canBook({ start: 660, end: 690, now: 540, blocked: false, bookings })).toBe(true);
});

it("BUG-B: an available non-touching request leaves booking data unchanged (AC5)", () => {
  const bookings: Booking[] = [{ start: 600, end: 660 }];
  const before = structuredClone(bookings);

  expect(canBook({ start: 720, end: 780, now: 540, blocked: false, bookings })).toBe(true);
  expect(bookings).toEqual(before);
});

const NOW = 540;

/**
 * Creates a fresh bookings fixture for every test.
 * The default existing booking is 600–660.
 */
function makeBookings(): Booking[] {
  return [{ start: 600, end: 660 }];
}

describe("canBook — AC1: valid interval and future start", () => {
  it("AC1: rejects a start before minute zero independently of the current time", () => {
    expect(canBook({ start: -1, end: 60, now: -10, blocked: false, bookings: [] })).toBe(false);
  });

  it("AC1: accepts a request starting one minute after now", () => {
    expect(canBook({ start: 541, end: 542, now: NOW, blocked: false, bookings: [] })).toBe(true);
  });

  it("AC1: accepts a one-minute interval", () => {
    expect(canBook({ start: 720, end: 721, now: NOW, blocked: false, bookings: [] })).toBe(true);
  });

  it("T02: rejects a request that starts exactly now", () => {
    const bookings = makeBookings();

    expect(
      canBook({
        start: 540,
        end: 570,
        now: NOW,
        blocked: false,
        bookings,
      }),
    ).toBe(false);
  });

  it("T03: rejects zero-duration interval", () => {
    const bookings = makeBookings();

    expect(
      canBook({
        start: 720,
        end: 720,
        now: NOW,
        blocked: false,
        bookings,
      }),
    ).toBe(false);
  });

  it("T04: rejects reversed interval", () => {
    const bookings = makeBookings();

    expect(
      canBook({
        start: 750,
        end: 720,
        now: NOW,
        blocked: false,
        bookings,
      }),
    ).toBe(false);
  });

  it("T05: rejects an end time after minute 1440", () => {
    const bookings = makeBookings();

    expect(
      canBook({
        start: 1380,
        end: 1441,
        now: NOW,
        blocked: false,
        bookings,
      }),
    ).toBe(false);
  });

  it("X1: accepts an interval ending exactly at minute 1440", () => {
    const bookings = makeBookings();

    expect(
      canBook({
        start: 1380,
        end: 1440,
        now: NOW,
        blocked: false,
        bookings,
      }),
    ).toBe(true);
  });
});

describe("canBook — AC2: maximum duration is 120 minutes", () => {
  it("T06: accepts exactly 120 minutes", () => {
    const bookings = makeBookings();

    expect(
      canBook({
        start: 720,
        end: 840,
        now: NOW,
        blocked: false,
        bookings,
      }),
    ).toBe(true);
  });

  it("T07: rejects 121 minutes", () => {
    const bookings = makeBookings();

    expect(
      canBook({
        start: 720,
        end: 841,
        now: NOW,
        blocked: false,
        bookings,
      }),
    ).toBe(false);
  });
});

describe("canBook — AC3: blocked rooms", () => {
  it("T13: rejects an otherwise available request when room is blocked", () => {
    const bookings = makeBookings();

    expect(
      canBook({
        start: 660,
        end: 720,
        now: NOW,
        blocked: true,
        bookings,
      }),
    ).toBe(false);
  });
});

describe("canBook — AC4: overlap detection", () => {
  it("T01: accepts touching after an existing booking", () => {
    const bookings = makeBookings();

    expect(
      canBook({
        start: 660,
        end: 720,
        now: NOW,
        blocked: false,
        bookings,
      }),
    ).toBe(true);
  });

  it("T08: accepts touching before an existing booking", () => {
    const bookings = makeBookings();

    expect(
      canBook({
        start: 570,
        end: 600,
        now: NOW,
        blocked: false,
        bookings,
      }),
    ).toBe(true);
  });

  it("T09: rejects partial overlap", () => {
    const bookings = makeBookings();

    expect(
      canBook({
        start: 630,
        end: 690,
        now: NOW,
        blocked: false,
        bookings,
      }),
    ).toBe(false);
  });

  it("T10: rejects a request containing an existing booking", () => {
    const bookings = makeBookings();

    expect(
      canBook({
        start: 570,
        end: 690,
        now: NOW,
        blocked: false,
        bookings,
      }),
    ).toBe(false);
  });

  it("T11: rejects a request fully inside an existing booking", () => {
    const bookings = makeBookings();

    expect(
      canBook({
        start: 615,
        end: 645,
        now: NOW,
        blocked: false,
        bookings,
      }),
    ).toBe(false);
  });

  it("T12: rejects an interval identical to an existing booking", () => {
    const bookings = makeBookings();

    expect(
      canBook({
        start: 600,
        end: 660,
        now: NOW,
        blocked: false,
        bookings,
      }),
    ).toBe(false);
  });

  it("T14: accepts the request when there are no existing bookings", () => {
    const bookings: Booking[] = [];

    expect(
      canBook({
        start: 630,
        end: 690,
        now: NOW,
        blocked: false,
        bookings,
      }),
    ).toBe(true);
  });

  it("X2: accepts an interval touching two bookings at both endpoints", () => {
    const bookings: Booking[] = [
      { start: 600, end: 660 },
      { start: 720, end: 780 },
    ];

    expect(
      canBook({
        start: 660,
        end: 720,
        now: NOW,
        blocked: false,
        bookings,
      }),
    ).toBe(true);
  });
});

describe("canBook — AC5: Boolean result and no input mutation", () => {
  it("AC5: returns true and leaves booking data unchanged for an available request", () => {
    const bookings: Booking[] = [
      { start: 600, end: 660 },
      { start: 800, end: 850 },
    ];

    const before = structuredClone(bookings);

    const result = canBook({
      start: 660,
      end: 720,
      now: NOW,
      blocked: false,
      bookings,
    });

    expect(result).toBe(true);
    expect(typeof result).toBe("boolean");
    expect(bookings).toEqual(before);
  });

  it("AC5: leaves booking data unchanged when the request is rejected", () => {
    const bookings: Booking[] = [
      { start: 600, end: 660 },
      { start: 800, end: 850 },
    ];

    const before = structuredClone(bookings);

    const result = canBook({
      start: 630,
      end: 690,
      now: NOW,
      blocked: false,
      bookings,
    });

    expect(result).toBe(false);
    expect(typeof result).toBe("boolean");
    expect(bookings).toEqual(before);
  });
});

it("R3 AC1: rejects fractional minutes for start or end time", () => {
  const bookings: Booking[] = [];
  expect(
    canBook({
      start: 600.5,
      end: 660,
      now: 540,
      blocked: false,
      bookings,
    }),
  ).toBe(false);
  expect(
    canBook({
      start: 600,
      end: 660.25,
      now: 540,
      blocked: false,
      bookings,
    }),
  ).toBe(false);
});

