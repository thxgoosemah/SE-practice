export interface Booking {
  start: number; // minutes from midnight, [0, 1440)
  end: number; // minutes from midnight, (0, 1440]
  label?: string;
}

export interface Room {
  id: string;
  name: string;
  building: string;
  floor: number;
  capacity: number;
  type: string;
  blocked: boolean;
  bookings: Booking[];
}

export type Decision = "available" | "unavailable" | "invalid";

export interface CheckInput {
  room: Room;
  currentTimeMin: number;
  startMin: number;
  endMin: number;
}

export interface CheckResult {
  decision: Decision;
  reason: string;
  /** Conflict details when unavailable due to overlap (AC4). */
  conflict?: Booking;
}
