import { useMemo, useState } from "react";
import {
  CalendarCheck,
  Clock,
  DoorClosed,
  DoorOpen,
  Info,
  MapPin,
  Users,
  CheckCircle2,
  XCircle,
  AlertTriangle,
} from "lucide-react";
import { BOOKINGS, ROOMS } from "@/data";
import {
  checkAvailability,
  labelToMinutes,
  minutesToLabel,
} from "@/availability";
import type { CheckResult } from "@/types";

function useNowMinutes(): number {
  const now = new Date();
  return now.getHours() * 60 + now.getMinutes();
}

export default function App() {
  const nowMinutes = useNowMinutes();
  const [roomId, setRoomId] = useState<string>(ROOMS[0].id);
  const [startLabel, setStartLabel] = useState<string>("");
  const [endLabel, setEndLabel] = useState<string>("");
  const [submitted, setSubmitted] = useState(false);

  const room = useMemo(
    () => ROOMS.find((r) => r.id === roomId),
    [roomId]
  );
  const roomBookings = useMemo(
    () => BOOKINGS.filter((b) => b.roomId === roomId),
    [roomId]
  );

  const result: CheckResult | null = useMemo(() => {
    if (!submitted) return null;
    const start = labelToMinutes(startLabel);
    const end = labelToMinutes(endLabel);
    return checkAvailability(
      room,
      roomBookings,
      { start: start ?? NaN, end: end ?? NaN },
      nowMinutes
    );
  }, [submitted, startLabel, endLabel, room, roomBookings, nowMinutes]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitted(true);
  }

  function handleReset() {
    setStartLabel("");
    setEndLabel("");
    setSubmitted(false);
  }

  const isAvailable = result?.decision === "Available";

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <div className="mx-auto max-w-5xl px-4 py-8 sm:py-12">
        <header className="mb-8 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-600 text-white shadow-sm">
            <CalendarCheck className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">
              Smart Campus Room Availability
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Check whether a room is free for your proposed time slot. This
              prototype does not save or confirm bookings.
            </p>
          </div>
        </header>

        <div className="grid gap-6 lg:grid-cols-5">
          {/* Form panel */}
          <section className="lg:col-span-3 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
            <h2 className="text-lg font-semibold text-slate-900">
              Check a room
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              Current time:{" "}
              <span className="font-medium text-slate-700">
                {minutesToLabel(nowMinutes)}
              </span>
              . Intervals include the start minute and exclude the end minute.
            </p>

            <form onSubmit={handleSubmit} className="mt-5 space-y-5">
              <div>
                <label
                  htmlFor="room"
                  className="block text-sm font-medium text-slate-700"
                >
                  Room
                </label>
                <select
                  id="room"
                  value={roomId}
                  onChange={(e) => {
                    setRoomId(e.target.value);
                    setSubmitted(false);
                  }}
                  className="mt-1.5 block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 shadow-sm transition focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
                >
                  {ROOMS.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.name}
                      {r.blocked ? " — Blocked" : ""}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <TimeField
                  id="start"
                  label="Start time (HH:MM)"
                  value={startLabel}
                  onChange={(v) => {
                    setStartLabel(v);
                    setSubmitted(false);
                  }}
                />
                <TimeField
                  id="end"
                  label="End time (HH:MM)"
                  value={endLabel}
                  onChange={(v) => {
                    setEndLabel(v);
                    setSubmitted(false);
                  }}
                />
              </div>

              <div className="flex flex-wrap gap-3 pt-1">
                <button
                  type="submit"
                  className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-300"
                >
                  <CheckCircle2 className="h-4 w-4" />
                  Check availability
                </button>
                <button
                  type="button"
                  onClick={handleReset}
                  className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-200"
                >
                  Clear
                </button>
              </div>
            </form>

            {result && (
              <ResultBanner
                available={isAvailable}
                reasons={result.reasons}
                startLabel={startLabel}
                endLabel={endLabel}
              />
            )}
          </section>

          {/* Room info + schedule */}
          <aside className="lg:col-span-2 space-y-6">
            <RoomCard room={room} />
            <ScheduleCard
              bookings={roomBookings}
              blocked={room?.blocked ?? false}
            />
          </aside>
        </div>

        <footer className="mt-10 text-center text-xs text-slate-400">
          Fictional sample data for prototype use only.
        </footer>
      </div>
    </div>
  );
}

function TimeField({
  id,
  label,
  value,
  onChange,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <label
        htmlFor={id}
        className="block text-sm font-medium text-slate-700"
      >
        {label}
      </label>
      <input
        id={id}
        type="text"
        inputMode="numeric"
        placeholder="e.g. 14:30"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1.5 block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 shadow-sm transition placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
      />
    </div>
  );
}

function ResultBanner({
  available,
  reasons,
  startLabel,
  endLabel,
}: {
  available: boolean;
  reasons: string[];
  startLabel: string;
  endLabel: string;
}) {
  if (available) {
    return (
      <div className="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
        <div className="flex items-start gap-3">
          <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-600" />
          <div>
            <p className="font-semibold text-emerald-800">
              Available — {startLabel} to {endLabel}
            </p>
            <p className="mt-1 text-sm text-emerald-700">
              This time slot is free and satisfies all booking rules. No booking
              has been saved.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 p-4">
      <div className="flex items-start gap-3">
        <XCircle className="mt-0.5 h-5 w-5 shrink-0 text-rose-600" />
        <div className="w-full">
          <p className="font-semibold text-rose-800">
            Unavailable — {startLabel || "?"} to {endLabel || "?"}
          </p>
          <ul className="mt-2 space-y-1 text-sm text-rose-700">
            {reasons.map((r, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="mt-1.5 inline-block h-1 w-1 shrink-0 rounded-full bg-rose-500" />
                {r}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

function RoomCard({ room }: { room: ReturnType<typeof ROOMS.find> }) {
  if (!room) return null;
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-900">
          Room details
        </h3>
        {room.blocked ? (
          <span className="inline-flex items-center gap-1 rounded-full bg-rose-100 px-2.5 py-0.5 text-xs font-medium text-rose-700">
            <DoorClosed className="h-3.5 w-3.5" /> Blocked
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-medium text-emerald-700">
            <DoorOpen className="h-3.5 w-3.5" /> Open
          </span>
        )}
      </div>
      <dl className="mt-3 space-y-2 text-sm">
        <div className="flex items-center gap-2 text-slate-600">
          <MapPin className="h-4 w-4 text-slate-400" />
          <span>{room.building}</span>
        </div>
        <div className="flex items-center gap-2 text-slate-600">
          <Users className="h-4 w-4 text-slate-400" />
          <span>Capacity: {room.capacity}</span>
        </div>
      </dl>
      {room.blocked && room.blockedReason && (
        <div className="mt-3 flex items-start gap-2 rounded-lg bg-amber-50 p-3 text-xs text-amber-800">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-500" />
          <span>{room.blockedReason}</span>
        </div>
      )}
    </div>
  );
}

function ScheduleCard({
  bookings,
  blocked,
}: {
  bookings: { id: string; title: string; start: number; end: number }[];
  blocked: boolean;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-2">
        <Clock className="h-4 w-4 text-slate-400" />
        <h3 className="text-base font-semibold text-slate-900">
          Today&apos;s schedule
        </h3>
      </div>
      {blocked ? (
        <p className="mt-3 flex items-start gap-2 text-sm text-slate-500">
          <Info className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
          Room is blocked; schedule is informational only.
        </p>
      ) : bookings.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">
          No existing bookings today.
        </p>
      ) : (
        <ul className="mt-3 space-y-2">
          {bookings
            .sort((a, b) => a.start - b.start)
            .map((b) => (
              <li
                key={b.id}
                className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-sm"
              >
                <span className="font-medium text-slate-700">{b.title}</span>
                <span className="tabular-nums text-slate-500">
                  {minutesToLabel(b.start)}–{minutesToLabel(b.end)}
                </span>
              </li>
            ))}
        </ul>
      )}
    </div>
  );
}
