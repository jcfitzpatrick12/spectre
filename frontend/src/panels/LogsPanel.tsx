import { useMemo, useState } from 'react';
import { Panel } from '../components/Panel';
import { Modal } from '../components/Modal';
import { Button } from '../components/Button';
import { TextInput, Select } from '../components/Field';
import { useLogFiles, useLogRaw } from '../api/queries';
import './list-common.css';

interface Filter {
  year?: number;
  month?: number;
  day?: number;
  process_type?: string;
}

function parseInt10(v: string): number | undefined {
  if (!v.trim()) return undefined;
  const n = Number.parseInt(v, 10);
  return Number.isFinite(n) ? n : undefined;
}

function LogViewer({
  fileName,
  onClose,
}: {
  fileName: string;
  onClose: () => void;
}) {
  const { data, isLoading, error } = useLogRaw(fileName);
  return (
    <Modal title={`LOG · ${fileName}`} onClose={onClose} wide>
      {isLoading && <div className="dim">LOADING…</div>}
      {error && <div className="err">FAIL — {String(error)}</div>}
      {data !== undefined && (
        <pre
          style={{
            margin: 0,
            fontFamily: 'var(--font-mono)',
            fontSize: 12,
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            maxHeight: '65vh',
            overflow: 'auto',
          }}
        >
          {data}
        </pre>
      )}
    </Modal>
  );
}

export function LogsPanel() {
  const [pending, setPending] = useState<Filter>({});
  const [applied, setApplied] = useState<Filter>({});
  const [selected, setSelected] = useState<string | null>(null);

  const filter = useMemo(
    () => ({
      year: applied.year,
      month: applied.month,
      day: applied.day,
      process_type: applied.process_type ? [applied.process_type] : undefined,
    }),
    [applied],
  );
  const { data, isLoading, error, refetch, isFetching } = useLogFiles(filter);

  return (
    <Panel title="LOGS" span={6}>
      <div className="filter-row">
        <TextInput
          label="YEAR"
          name="year"
          inputMode="numeric"
          placeholder="—"
          value={pending.year ?? ''}
          onChange={(e) => setPending({ ...pending, year: parseInt10(e.target.value) })}
          style={{ width: 60 }}
        />
        <TextInput
          label="MONTH"
          name="month"
          inputMode="numeric"
          placeholder="—"
          value={pending.month ?? ''}
          onChange={(e) => setPending({ ...pending, month: parseInt10(e.target.value) })}
          style={{ width: 60 }}
        />
        <TextInput
          label="DAY"
          name="day"
          inputMode="numeric"
          placeholder="—"
          value={pending.day ?? ''}
          onChange={(e) => setPending({ ...pending, day: parseInt10(e.target.value) })}
          style={{ width: 60 }}
        />
        <Select
          label="PROC"
          name="process_type"
          value={pending.process_type ?? ''}
          onChange={(e) =>
            setPending({ ...pending, process_type: e.target.value || undefined })
          }
          style={{ width: 90 }}
        >
          <option value="">any</option>
          <option value="worker">worker</option>
          <option value="user">user</option>
        </Select>
        <Button size="sm" onClick={() => setApplied(pending)}>APPLY</Button>
        <Button
          size="sm"
          tone="dim"
          onClick={() => {
            setPending({});
            setApplied({});
          }}
        >
          CLEAR
        </Button>
        <Button size="sm" tone="dim" onClick={() => refetch()} disabled={isFetching}>
          {isFetching ? 'REFRESHING' : 'REFRESH'}
        </Button>
      </div>

      {isLoading && <div className="dim">LOADING…</div>}
      {error && <div className="err">FAIL — {String(error)}</div>}
      {data && data.length === 0 && <div className="dim">— NO LOGS —</div>}

      <div className="list">
        {data?.map((name) => (
          <button
            key={name}
            type="button"
            className={`list-row ${selected === name ? 'list-row--selected' : ''}`}
            onClick={() => setSelected(name)}
            title={name}
          >
            <span className="list-row__name">{name}</span>
          </button>
        ))}
      </div>

      {selected && <LogViewer fileName={selected} onClose={() => setSelected(null)} />}
    </Panel>
  );
}
