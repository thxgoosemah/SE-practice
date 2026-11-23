import { useMemo, useState } from "react";
import type { CheckResult, Room } from "./types";
import { SAMPLE_ROOMS } from "./data/rooms";
import { checkAvailability } from "./lib/checkAvailability";
import { canBook } from "./booking";
import { fmtTime, nowHHMM, parseTime } from "./lib/time";
import { RoomSelector } from "./components/RoomSelector";
import { BookingForm } from "./components/BookingForm";
import { RoomTimeline } from "./components/RoomTimeline";
import { DecisionPanel } from "./components/DecisionPanel";

function App() {
  const [selectedId, setSelectedId] = useState(SAMPLE_ROOMS[0].id);
  const [currentTime, setCurrentTime] = useState(nowHHMM());
  const [startTime, setStartTime] = useState("10:00");
  const [endTime, setEndTime] = useState("11:00");
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<CheckResult | null>(null);

  const room: Room =
    SAMPLE_ROOMS.find((r) => r.id === selectedId) ?? SAMPLE_ROOMS[0];

  const candidate = useMemo(() => {
    const s = parseTime(startTime);
    const e = parseTime(endTime);
    if (Number.isNaN(s) || Number.isNaN(e)) return null;
    return { start: s, end: e };
  }, [startTime, endTime]);

  const clearResult = () => {
    setResult(null);
    setSubmitted(false);
  };

  const handleSubmit = () => {
    const current = parseTime(currentTime);
    const start = parseTime(startTime);
    const end = parseTime(endTime);
    const isAvailable = canBook({
      start,
      end,
      now: current,
      blocked: room.blocked,
      bookings: room.bookings,
    });
    const res = checkAvailability({
      room,
      currentTimeMin: current,
      startMin: start,
      endMin: end,
    });
    // canBook controls availability; retain the detailed validation feedback.
    setResult({
      ...res,
      decision: isAvailable
        ? "available"
        : res.decision === "invalid" ? "invalid" : "unavailable",
    });
    setSubmitted(true);
  };

  const handleReset = () => {
    setCurrentTime(nowHHMM());
    setStartTime("10:00");
    setEndTime("11:00");
    clearResult();
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true">
            <span className="brand-dot" />
          </div>
          <div>
            <h1>Smart Campus</h1>
            <p className="brand-sub">Room Availability Checker</p>
          </div>
        </div>
        <p className="tagline">
          Check whether a time slot is available on a campus room. Read-only —
          no booking is created.
        </p>
      </header>

      <main className="layout">
        <section className="panel left-panel" aria-label="Rooms">
          <h2 className="panel-title">Select a room</h2>
          <RoomSelector
            rooms={SAMPLE_ROOMS}
            selectedId={selectedId}
            onSelect={(id) => {
              setSelectedId(id);
              clearResult();
            }}
          />
        </section>

        <section className="panel right-panel" aria-label="Availability check">
          <div className="room-summary">
            <div>
              <h2 className="room-summary-name">{room.name}</h2>
              <p className="room-summary-meta">
                {room.building} · Floor {room.floor} · Cap {room.capacity} · {room.type}
              </p>
            </div>
            {room.blocked && <span className="blocked-tag">Blocked</span>}
          </div>

          <BookingForm
            currentTime={currentTime}
            startTime={startTime}
            endTime={endTime}
            onCurrentTime={(v) => {
              setCurrentTime(v);
              clearResult();
            }}
            onStartTime={(v) => {
              setStartTime(v);
              clearResult();
            }}
            onEndTime={(v) => {
              setEndTime(v);
              clearResult();
            }}
            onSubmit={handleSubmit}
            onReset={handleReset}
          />

          <div className="timeline-section">
            <h3 className="section-title">Today's schedule</h3>
            <RoomTimeline
              bookings={room.bookings}
              candidate={candidate}
              blocked={room.blocked}
            />
          </div>

          <DecisionPanel result={result} submitted={submitted} />

          {room.bookings.length > 0 && (
            <ul className="booking-list">
              {room.bookings.map((b, i) => (
                <li key={i}>
                  <span className="booking-list-time">
                    {fmtTime(b.start)}–{fmtTime(b.end)}
                  </span>
                  {b.label && <span className="booking-list-label">{b.label}</span>}
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>

      <footer className="app-footer">
        Fictional sample data · Read-only availability check
      </footer>
    </div>
  );
}

export default App;
