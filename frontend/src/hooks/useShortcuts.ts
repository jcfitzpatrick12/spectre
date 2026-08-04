import { useEffect } from 'react';

/**
 * Very small keyboard-shortcut layer. Shortcuts are inert when the user is
 * typing into a text input, textarea, or contenteditable element (except
 * for `/` which acts as a common "focus filter" convention).
 */
export function useShortcuts() {
  useEffect(() => {
    const focusById = (id: string) => {
      const el = document.getElementById(id);
      if (!el) return;
      (el as HTMLElement).scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      (el as HTMLElement).focus();
    };

    const clickById = (id: string) => {
      const el = document.getElementById(id);
      if (!el) return;
      (el as HTMLElement).scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      (el as HTMLElement).click();
    };

    const isTyping = (target: EventTarget | null): boolean => {
      if (!(target instanceof HTMLElement)) return false;
      const tag = target.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return true;
      return target.isContentEditable;
    };

    const onKey = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const typing = isTyping(e.target);
      if (e.key === '/') {
        e.preventDefault();
        focusById('batches-filter-tag');
        return;
      }
      if (typing) return;
      switch (e.key.toLowerCase()) {
        case 'r':
          e.preventDefault();
          focusById('rec-duration');
          break;
        case 'n':
          e.preventDefault();
          clickById('cfg-new');
          break;
      }
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, []);
}
