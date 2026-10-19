import type { Booking, Room } from "@/types";

export const ROOMS: Room[] = [
  {
    id: "room-101",
    name: "Thompson Hall 101",
    building: "Thompson Hall",
    capacity: 30,
    blocked: false,
  },
  {
    id: "room-204",
    name: "Thompson Hall 204",
    building: "Thompson Hall",
    capacity: 18,
    blocked: true,
    blockedReason: "Maintenance — HVAC repair scheduled for today.",
  },
  {
    id: "lab-a",
    name: "Engineering Lab A",
    building: "Foster Engineering Center",
    capacity: 24,
    blocked: false,
  },
];

export const BOOKINGS: Booking[] = [
  { id: "b1", roomId: "room-101", title: "Intro to Algorithms", start: 540, end: 630 }, // 09:00–10:30
  { id: "b2", roomId: "room-101", title: "Study Group", start: 1080, end: 1140 }, // 18:00–19:00
  { id: "b3", roomId: "lab-a", title: "Robotics Workshop", start: 720, end: 840 }, // 12:00–14:00
  { id: "b4", roomId: "lab-a", title: "Office Hours", start: 960, end: 1020 }, // 16:00–17:00
];
