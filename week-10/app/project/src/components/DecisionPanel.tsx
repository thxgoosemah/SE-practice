import type { CheckResult } from "../types";

interface DecisionPanelProps {
  result: CheckResult | null;
  submitted: boolean;
}

const DECISION_META = {
  available: {
    title: "Available",
    className: "decision-available",
    icon: "✓",
  },
  unavailable: {
    title: "Unavailable",
    className: "decision-unavailable",
    icon: "✕",
  },
  invalid: {
    title: "Check your input",
    className: "decision-invalid",
    icon: "!",
  },
} as const;

export function DecisionPanel({ result, submitted }: DecisionPanelProps) {
  if (!submitted || !result) {
    return (
      <div className="decision-panel empty">
        <p className="decision-placeholder">
 Choose a room, set a current time and a start–end interval, then select Check availability.
        </p>
      </div>
    );
  }

  const meta = DECISION_META[result.decision];
  return (
    <div className={`decision-panel ${meta.className}`} role="status" aria-live="polite">
      <div className="decision-head">
        <span className="decision-icon" aria-hidden="true">{meta.icon}</span>
        <div>
          <h2 className="decision-title">{meta.title}</h2>
          <p className="decision-reason">{result.reason}</p>
        </div>
      </div>
      <p className="decision-note">
        This is a read-only check — existing bookings are not modified.
      </p>
    </div>
  );
}
