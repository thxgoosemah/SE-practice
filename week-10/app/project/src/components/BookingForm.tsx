interface BookingFormProps {
  currentTime: string;
  startTime: string;
  endTime: string;
  onCurrentTime: (v: string) => void;
  onStartTime: (v: string) => void;
  onEndTime: (v: string) => void;
  onSubmit: () => void;
  onReset: () => void;
}

export function BookingForm({
  currentTime,
  startTime,
  endTime,
  onCurrentTime,
  onStartTime,
  onEndTime,
  onSubmit,
  onReset,
}: BookingFormProps) {
  return (
    <form
      className="booking-form"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
    >
      <div className="form-row">
        <label className="field">
          <span className="field-label">Current time</span>
          <input
            type="time"
            value={currentTime}
            onChange={(e) => onCurrentTime(e.target.value)}
            required
          />
        </label>
        <label className="field">
          <span className="field-label">Start</span>
          <input
            type="time"
            value={startTime}
            onChange={(e) => onStartTime(e.target.value)}
            required
          />
        </label>
        <label className="field">
          <span className="field-label">End</span>
          <input
            type="time"
            value={endTime}
            onChange={(e) => onEndTime(e.target.value)}
            required
          />
        </label>
      </div>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary">
          Check availability
        </button>
        <button type="button" className="btn btn-ghost" onClick={onReset}>
          Reset
        </button>
      </div>
      <p className="form-hint">
        Max length 120 min. Intervals use a 24-hour clock (00:00–24:00). Touching
        endpoints are allowed.
      </p>
    </form>
  );
}
