import type { Booking } from "../types";
import { fmtTime } from "../lib/time";

interface RoomTimelineProps {
  bookings: Booking[];
  candidate?: { start: number; end: number } | null;
  blocked: boolean;
}

// Hours to mark on the axis.
const HOURS = Array.from({ length: 25 }, (_, i) => i); // 0..24

export function RoomTimeline({ bookings, candidate, blocked }: RoomTimelineProps) {
  return (
    <div className="timeline">
      <div className="timeline-track">
        {/* hour gridlines */}
        {HOURS.map((h) => (
          <div
            key={h}
            className="timeline-grid"
            style={{ left: `${(h / 24) * 100}%` }}
          />
        ))}

        {/* existing bookings */}
        {bookings.map((b, i) => (
          <div
            key={i}
            className="timeline-booking"
            style={{
              left: `${(b.start / 1440) * 100}%`,
              width: `${((b.end - b.start) / 1440) * 100}%`,
            }}
            title={`${fmtTime(b.start)}–${fmtTime(b.end)}${b.label ? ` · ${b.label}` : ""}`}
          >
            <span>{b.label || `${fmtTime(b.start)}`}</span>
          </div>
        ))}

        {/* candidate interval */}
        {candidate && candidate.end > candidate.start && (
          <div
            className={`timeline-candidate ${blocked ? "blocked" : ""}`}
            style={{
              left: `${(Math.max(0, candidate.start) / 1440) * 100}%`,
              width: `${Math.min(
                100,
                ((Math.min(1440, candidate.end) - Math.max(0, candidate.start)) /
                  1440) *
                  100
              )}%`,
            }}
          />
        )}
      </div>

      <div className="timeline-axis">
        {HOURS.filter((h) => h % 6 === 0).map((h) => (
          <span key={h} style={{ left: `${(h / 24) * 100}%` }}>
            {fmtTime(h * 60)}
          </span>
        ))}
      </div>

      <div className="timeline-legend">
        <span className="legend-item">
          <span className="legend-swatch existing" /> Existing booking
        </span>
        <span className="legend-item">
          <span className="legend-swatch candidate" /> Your request
        </span>
      </div>
    </div>
  );
}
