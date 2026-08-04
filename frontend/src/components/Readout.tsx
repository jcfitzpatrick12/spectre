import type { ReactNode } from 'react';
import './Readout.css';

export interface ReadoutRow {
  label: string;
  value: ReactNode;
  tone?: 'default' | 'accent' | 'dim';
}

export interface ReadoutProps {
  rows: ReadoutRow[];
}

/**
 * The stacked ACC/BAK/LAST/MODE/IDLE-style meter column intended to sit in
 * a Panel's `readout` slot.
 */
export function Readout({ rows }: ReadoutProps) {
  return (
    <div className="readout">
      {rows.map((row) => (
        <div key={row.label} className={`readout__row readout__row--${row.tone ?? 'default'}`}>
          <div className="readout__label">{row.label}</div>
          <div className="readout__value">{row.value}</div>
        </div>
      ))}
    </div>
  );
}
