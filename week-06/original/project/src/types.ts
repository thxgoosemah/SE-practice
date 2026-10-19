export interface Room {
  id: string;
  name: string;
  building: string;
  capacity: number;
  blocked: boolean;
  blockedReason?: string;
}

export interface Booking {
  id: string;
  roomId: string;
  title: string;
  start: number; // minutes from 00:00, inclusive
  end: number; // minutes from 00:00, exclusive
}

export interface IntervalInput {
  start: number;
  end: number;
}

export type Decision = "Available" | "Unavailable";

export interface CheckResult {
  decision: Decision;
  reasons: string[];
}

export const MINUTES_PER_DAY = 1440;
export const MAX_BOOKING_MINUTES = 120;
