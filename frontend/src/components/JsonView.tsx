import './JsonView.css';

export interface JsonViewProps {
  value: unknown;
  className?: string;
}

/**
 * Minimal, dependency-free JSON pretty-printer. Renders as monospaced text
 * with two-space indent. No syntax highlighting to keep the aesthetic austere.
 */
export function JsonView({ value, className }: JsonViewProps) {
  let text: string;
  try {
    text = JSON.stringify(value, null, 2);
  } catch {
    text = String(value);
  }
  return <pre className={`json-view ${className ?? ''}`}>{text}</pre>;
}
