import { clsx } from 'clsx';
import type { ButtonHTMLAttributes, ReactNode } from 'react';
import './Button.css';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  tone?: 'default' | 'accent' | 'dim';
  size?: 'sm' | 'md';
}

/**
 * Hard-edged bracketed button, [ RUN ]-style. Renders label wrapped in
 * brackets so the aesthetic is preserved even in dense layouts.
 */
export function Button({
  children,
  tone = 'default',
  size = 'md',
  className,
  type = 'button',
  ...rest
}: ButtonProps) {
  return (
    <button
      {...rest}
      type={type}
      className={clsx('btn', `btn--${tone}`, `btn--${size}`, className)}
    >
      <span className="btn__bracket">[</span>
      <span className="btn__label">{children}</span>
      <span className="btn__bracket">]</span>
    </button>
  );
}
