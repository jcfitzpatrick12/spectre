import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { spectreFetch, SpectreApiError } from './api/client';
import { ReceiversPanel } from './panels/ReceiversPanel';
import { ConfigsPanel } from './panels/ConfigsPanel';
import { BatchesPanel } from './panels/BatchesPanel';
import { LogsPanel } from './panels/LogsPanel';
import { SpectrogramPanel } from './panels/SpectrogramPanel';
import { ConfigEditorPanel } from './panels/ConfigEditorPanel';
import { RecordPanel } from './panels/RecordPanel';
import { LogStreamPanel } from './panels/LogStreamPanel';
import { RecordingIndicator } from './components/RecordingIndicator';
import { useShortcuts } from './hooks/useShortcuts';

/**
 * Piggy-backs on the `['receivers']` cache key used by `useReceivers`, adding
 * a 20s poll interval as the app-wide health probe. React Query merges
 * observer options per key, so this stays a single request.
 */
function StatusChip() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['receivers'],
    queryFn: () => spectreFetch<string[]>('/receivers'),
    retry: 0,
    refetchInterval: 20_000,
  });
  if (isLoading) return <span style={{ color: 'var(--dim)' }}>PROBING</span>;
  if (error) {
    const msg = error instanceof SpectreApiError ? error.message : 'OFFLINE';
    return <span style={{ color: 'var(--accent)' }}>OFFLINE — {msg}</span>;
  }
  return (
    <span style={{ color: 'var(--fg)' }}>
      ONLINE · {data?.length ?? 0} RECEIVERS
    </span>
  );
}

export default function App() {
  const [selectedConfig, setSelectedConfig] = useState<string | null>(null);
  useShortcuts();

  return (
    <div className="app">
      <LogStreamPanel />

      <ReceiversPanel />

      <ConfigsPanel
        selectedFileName={selectedConfig}
        onSelect={setSelectedConfig}
      />

      <RecordPanel />

      <SpectrogramPanel />

      <BatchesPanel />

      <LogsPanel />

      <ConfigEditorPanel
        selectedFileName={selectedConfig}
        onSelectFileName={setSelectedConfig}
      />

      <footer
        style={{
          gridColumn: 'span 12',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: 11,
          color: 'var(--dim)',
          letterSpacing: 1,
          padding: '0 4px',
        }}
      >
        <span>SPECTRE FRONTEND v0.1</span>
        <StatusChip />
      </footer>

      <RecordingIndicator />
      <img className="watermark" src="/spectre.png" alt="" aria-hidden="true" />
    </div>
  );
}
