import { useEffect, useMemo, useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Panel } from '../components/Panel';
import { Readout } from '../components/Readout';
import { Button } from '../components/Button';
import { spectreFetch } from '../api/client';
import { fileNameFromEndpoint } from '../api/queries';
import { useRecordings } from '../state/RecordingsContext';
import './LogStreamPanel.css';

const TAIL_LINES = 40;
const POLL_MS = 2_000;

function today(): { year: number; month: number; day: number } {
  const d = new Date();
  return {
    year: d.getUTCFullYear(),
    month: d.getUTCMonth() + 1,
    day: d.getUTCDate(),
  };
}

function extractStamp(fileName: string): number {
  const m = fileName.match(/^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2}):(\d{2})/);
  if (!m) return 0;
  const [, date, hh, mm, ss] = m;
  return Date.parse(`${date}T${hh}:${mm}:${ss}Z`);
}

export function LogStreamPanel() {
  const { hasAnyInFlight } = useRecordings();
  const [manualTail, setManualTail] = useState(false);
  const [paused, setPaused] = useState(false);
  const tailing = (hasAnyInFlight || manualTail) && !paused;
  const scrollerRef = useRef<HTMLPreElement | null>(null);

  const scope = useMemo(today, []);

  const filesQuery = useQuery({
    queryKey: ['logstream', 'files', scope],
    queryFn: async () => {
      const endpoints = await spectreFetch<string[]>('/spectre-data/logs/', {
        query: {
          process_type: ['worker'],
          year: scope.year,
          month: scope.month,
          day: scope.day,
        },
      });
      return endpoints.map(fileNameFromEndpoint);
    },
    refetchInterval: tailing ? POLL_MS : false,
    enabled: tailing,
  });

  const newest = useMemo(() => {
    const files = filesQuery.data ?? [];
    if (files.length === 0) return null;
    let best = files[0]!;
    let bestStamp = extractStamp(best);
    for (const f of files) {
      const s = extractStamp(f);
      if (s > bestStamp) {
        best = f;
        bestStamp = s;
      }
    }
    return best;
  }, [filesQuery.data]);

  const rawQuery = useQuery({
    queryKey: ['logstream', 'raw', newest],
    queryFn: () =>
      spectreFetch<string>(
        `/spectre-data/logs/${encodeURIComponent(newest!)}/raw`,
      ),
    enabled: tailing && !!newest,
    refetchInterval: tailing ? POLL_MS : false,
  });

  const tailText = useMemo(() => {
    if (!rawQuery.data) return '';
    const lines = rawQuery.data.split(/\r?\n/);
    return lines.slice(-TAIL_LINES).join('\n');
  }, [rawQuery.data]);

  useEffect(() => {
    if (scrollerRef.current) {
      scrollerRef.current.scrollTop = scrollerRef.current.scrollHeight;
    }
  }, [tailText]);

  const mode = tailing ? 'TAIL' : paused ? 'PAUSE' : 'IDLE';
  const modeTone: 'accent' | 'dim' | 'default' =
    tailing ? 'accent' : 'dim';

  return (
    <Panel
      title="LOG STREAM"
      span={2}
      tone={tailing ? 'accent' : 'default'}
      readout={
        <Readout
          rows={[
            { label: 'MODE', value: mode, tone: modeTone },
          ]}
        />
      }
      actions={
        <>
          <Button
            size="sm"
            tone={manualTail ? 'accent' : 'dim'}
            onClick={() => setManualTail((v) => !v)}
          >
            {manualTail ? 'ON' : 'TAIL'}
          </Button>
          <Button
            size="sm"
            tone="dim"
            onClick={() => setPaused((v) => !v)}
            disabled={!hasAnyInFlight && !manualTail}
          >
            {paused ? 'RESUME' : 'PAUSE'}
          </Button>
        </>
      }
    >
      {!tailing && (
        <div className="dim" style={{ fontSize: 11 }}>
          {paused ? '— PAUSED —' : '— IDLE —'}
        </div>
      )}
      {tailing && !newest && (
        <div className="dim" style={{ fontSize: 11 }}>SCANNING…</div>
      )}
      {tailing && newest && (
        <div className="log-stream">
          <div className="log-stream__file">{newest}</div>
          <pre ref={scrollerRef} className="log-stream__pre">
            {tailText || '— WAITING —'}
            <span className="log-stream__cursor">▍</span>
          </pre>
        </div>
      )}
    </Panel>
  );
}
