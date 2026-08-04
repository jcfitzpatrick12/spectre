import { clsx } from 'clsx';
import type { ReactNode } from 'react';
import './Panel.css';

export interface PanelProps {
  title: string;
  children?: ReactNode;
  readout?: ReactNode;
  className?: string;
  actions?: ReactNode;
  /** Explicit column span (1-12). Applied as `grid-span-N`. */
  span?: 2 | 3 | 4 | 6 | 8 | 12;
  /** Optional accent state used for e.g. error highlighting. */
  tone?: 'default' | 'accent' | 'dim';
}

/**
 * The panel primitive. Renders a bordered box with a centred title chip and
 * an optional right-side readout column matching the TIS-100 meter style.
 */
export function Panel({
  title,
  children,
  readout,
  className,
  actions,
  span,
  tone = 'default',
}: PanelProps) {
  return (
    <section
      className={clsx(
        'panel',
        tone !== 'default' && `panel--${tone}`,
        span && `grid-span-${span}`,
        className,
      )}
    >
      <header className="panel__header">
        <span className="panel__title">— {title} —</span>
        {actions && <span className="panel__actions">{actions}</span>}
      </header>
      <div className="panel__body">
        <div className="panel__content">{children}</div>
        {readout && <aside className="panel__readout">{readout}</aside>}
      </div>
    </section>
  );
}
