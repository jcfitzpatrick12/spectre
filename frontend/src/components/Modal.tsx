import { useEffect } from 'react';
import type { ReactNode } from 'react';
import { clsx } from 'clsx';
import { Button } from './Button';
import './Modal.css';

export interface ModalProps {
  title: string;
  onClose: () => void;
  children: ReactNode;
  className?: string;
  wide?: boolean;
}

export function Modal({ title, onClose, children, className, wide }: ModalProps) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" onClick={onClose}>
      <div
        className={clsx('modal', wide && 'modal--wide', className)}
        onClick={(e) => e.stopPropagation()}
      >
        <header className="modal__header">
          <span className="modal__title">— {title} —</span>
          <Button size="sm" tone="dim" onClick={onClose}>CLOSE</Button>
        </header>
        <div className="modal__body">{children}</div>
      </div>
    </div>
  );
}
