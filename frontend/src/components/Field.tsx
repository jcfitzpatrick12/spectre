import { useId } from 'react';
import { clsx } from 'clsx';
import type { InputHTMLAttributes, SelectHTMLAttributes, ReactNode } from 'react';
import './Field.css';

export interface TextInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: ReactNode;
}

/** Hard-edged, underlined input. */
export function TextInput({ label, className, id, ...rest }: TextInputProps) {
  const autoId = useId();
  const inputId = id ?? autoId;
  return (
    <label className={clsx('field', className)} htmlFor={inputId}>
      {label && <span className="field__label">{label}</span>}
      <input {...rest} id={inputId} className="field__control" />
    </label>
  );
}

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: ReactNode;
  children: ReactNode;
}

export function Select({ label, className, id, children, ...rest }: SelectProps) {
  const autoId = useId();
  const selectId = id ?? autoId;
  return (
    <label className={clsx('field', className)} htmlFor={selectId}>
      {label && <span className="field__label">{label}</span>}
      <select {...rest} id={selectId} className="field__control field__control--select">
        {children}
      </select>
    </label>
  );
}
