import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import type { ReactNode } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { spectreFetch, SpectreApiError } from '../api/client';
import type { RecordingKind, RecordingRequest } from '../api/recordings';

/**
 * Tracks in-flight recordings client-side only. The backend has no status
 * endpoint (issue #192), so this state is best-effort: it dies with the tab
 * and cannot see recordings started elsewhere.
 */

export interface InFlightRecording {
  id: string;
  kind: RecordingKind;
  tags: string[];
  duration: number;
  startedAt: number;
}

export interface CompletedRecording {
  id: string;
  kind: RecordingKind;
  tags: string[];
  duration: number;
  startedAt: number;
  finishedAt: number;
  ok: boolean;
  message?: string;
  exitCode?: number;
}

interface Ctx {
  inFlight: InFlightRecording[];
  completed: CompletedRecording[];
  start: (req: RecordingRequest) => Promise<void>;
  /** Any of the given tags currently recording. */
  isRecordingAny: (tags: string[]) => boolean;
  hasAnyInFlight: boolean;
  dismissCompleted: (id: string) => void;
}

const Ctx = createContext<Ctx | null>(null);

let nextId = 1;
const genId = () => `rec-${nextId++}-${Date.now().toString(36)}`;

export function RecordingsProvider({ children }: { children: ReactNode }) {
  const [inFlight, setInFlight] = useState<InFlightRecording[]>([]);
  const [completed, setCompleted] = useState<CompletedRecording[]>([]);
  const qc = useQueryClient();
  // Persistent AbortController isn't useful — we never cancel — but this
  // keeps a stable reference the effect can inspect on unmount.
  const abortersRef = useRef<Map<string, AbortController>>(new Map());

  useEffect(
    () => () => {
      // Best-effort abort on unmount. The backend keeps recording either way.
      for (const c of abortersRef.current.values()) c.abort();
    },
    [],
  );

  const start = useCallback(
    async (req: RecordingRequest) => {
      const id = genId();
      const record: InFlightRecording = {
        id,
        kind: req.kind,
        tags: req.tags,
        duration: req.duration,
        startedAt: Date.now(),
      };
      setInFlight((r) => [...r, record]);
      const controller = new AbortController();
      abortersRef.current.set(id, controller);

      const path =
        req.kind === 'signal' ? '/recordings/signal' : '/recordings/spectrogram';

      try {
        const exit = await spectreFetch<number>(path, {
          method: 'POST',
          body: {
            tags: req.tags,
            duration: req.duration,
            force_restart: req.force_restart ?? false,
            max_restarts: req.max_restarts ?? 0,
            validate: req.validate ?? true,
          },
          signal: controller.signal,
        });
        setCompleted((c) => [
          {
            ...record,
            finishedAt: Date.now(),
            ok: exit === 0,
            exitCode: exit,
            message: exit === 0 ? 'complete' : `exit code ${exit}`,
          },
          ...c,
        ]);
      } catch (e) {
        const msg =
          e instanceof SpectreApiError
            ? e.message
            : e instanceof Error
              ? e.message
              : String(e);
        setCompleted((c) => [
          {
            ...record,
            finishedAt: Date.now(),
            ok: false,
            message: msg,
          },
          ...c,
        ]);
      } finally {
        setInFlight((r) => r.filter((x) => x.id !== id));
        abortersRef.current.delete(id);
        qc.invalidateQueries({ queryKey: ['batches'] });
        qc.invalidateQueries({ queryKey: ['logs'] });
        qc.invalidateQueries({ queryKey: ['batch-tags'] });
      }
    },
    [qc],
  );

  const isRecordingAny = useCallback(
    (tags: string[]) => {
      const active = new Set<string>(inFlight.flatMap((r) => r.tags));
      return tags.some((t) => active.has(t));
    },
    [inFlight],
  );

  const dismissCompleted = useCallback(
    (id: string) => setCompleted((c) => c.filter((x) => x.id !== id)),
    [],
  );

  const value = useMemo<Ctx>(
    () => ({
      inFlight,
      completed,
      start,
      isRecordingAny,
      hasAnyInFlight: inFlight.length > 0,
      dismissCompleted,
    }),
    [inFlight, completed, start, isRecordingAny, dismissCompleted],
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useRecordings(): Ctx {
  const v = useContext(Ctx);
  if (!v) throw new Error('useRecordings must be used inside RecordingsProvider');
  return v;
}
