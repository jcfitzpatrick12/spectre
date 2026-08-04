import { useEffect, useState } from 'react';
import { useRecordings } from '../state/RecordingsContext';
import './RecordingIndicator.css';

function formatElapsed(ms: number): string {
  const secs = Math.floor(ms / 1000);
  const mm = Math.floor(secs / 60).toString().padStart(2, '0');
  const ss = (secs % 60).toString().padStart(2, '0');
  return `${mm}:${ss}`;
}

/**
 * Fixed-position blinking pill in the top-right. One pill per in-flight
 * recording, showing tag(s) + client-side wall-clock timer.
 */
export function RecordingIndicator() {
  const { inFlight, completed, dismissCompleted } = useRecordings();
  const [tick, setTick] = useState(0);

  useEffect(() => {
    if (inFlight.length === 0) return;
    const id = window.setInterval(() => setTick((t) => t + 1), 500);
    return () => window.clearInterval(id);
  }, [inFlight.length]);

  // Auto-dismiss completed after 8s.
  useEffect(() => {
    if (completed.length === 0) return;
    const timers = completed.map((c) =>
      window.setTimeout(() => dismissCompleted(c.id), 8_000),
    );
    return () => timers.forEach(window.clearTimeout);
  }, [completed, dismissCompleted]);

  if (inFlight.length === 0 && completed.length === 0) return null;

  const now = Date.now();

  return (
    <div className="rec-indicator" data-tick={tick}>
      {inFlight.map((r) => (
        <div key={r.id} className="rec-indicator__chip rec-indicator__chip--live">
          <span className="rec-indicator__dot" />
          <span className="rec-indicator__label">
            REC · {r.kind === 'signal' ? 'SIG' : 'SPG'} · {r.tags.join(',')}
          </span>
          <span className="rec-indicator__time">
            {formatElapsed(now - r.startedAt)} / {formatElapsed(r.duration * 1000)}
          </span>
        </div>
      ))}
      {completed.map((c) => (
        <div
          key={c.id}
          className={`rec-indicator__chip rec-indicator__chip--${c.ok ? 'ok' : 'err'}`}
          onClick={() => dismissCompleted(c.id)}
          role="button"
          title="Dismiss"
        >
          <span className="rec-indicator__label">
            {c.ok ? 'DONE' : 'FAIL'} · {c.tags.join(',')}
          </span>
          <span className="rec-indicator__time">{c.message}</span>
        </div>
      ))}
    </div>
  );
}
