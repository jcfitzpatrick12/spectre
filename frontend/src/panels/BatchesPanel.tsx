import { useMemo, useState } from 'react';
import { Panel } from '../components/Panel';
import { Modal } from '../components/Modal';
import { Button } from '../components/Button';
import { TextInput } from '../components/Field';
import { useBatchFiles, batchFileUrl } from '../api/queries';
import './list-common.css';

interface Filter {
  year?: number;
  month?: number;
  day?: number;
  tag?: string;
  extension?: string;
}

function parseInt10(v: string): number | undefined {
  if (!v.trim()) return undefined;
  const n = Number.parseInt(v, 10);
  return Number.isFinite(n) ? n : undefined;
}

function extractDate(fileName: string): string {
  // File names look like: 2026-08-01T15:23:04_sun.h5
  const m = fileName.match(/^(\d{4}-\d{2}-\d{2})/);
  return m?.[1] ?? '—';
}

function extractExtension(fileName: string): string {
  const dot = fileName.lastIndexOf('.');
  return dot === -1 ? '' : fileName.slice(dot + 1).toLowerCase();
}

function BatchLightbox({
  fileName,
  onClose,
}: {
  fileName: string;
  onClose: () => void;
}) {
  return (
    <Modal title={`BATCH · ${fileName}`} onClose={onClose} wide>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <img
          src={batchFileUrl(fileName)}
          alt={fileName}
          style={{ maxWidth: '100%', maxHeight: '70vh', background: 'var(--track)' }}
        />
        <a href={batchFileUrl(fileName)} target="_blank" rel="noreferrer" download>
          DOWNLOAD
        </a>
      </div>
    </Modal>
  );
}

export function BatchesPanel() {
  const [pending, setPending] = useState<Filter>({});
  const [applied, setApplied] = useState<Filter>({});
  const [preview, setPreview] = useState<string | null>(null);

  const filter = useMemo(
    () => ({
      year: applied.year,
      month: applied.month,
      day: applied.day,
      tag: applied.tag ? [applied.tag] : undefined,
      extension: applied.extension ? [applied.extension] : undefined,
    }),
    [applied],
  );
  const { data, isLoading, error, refetch, isFetching } = useBatchFiles(filter);

  const grouped = useMemo(() => {
    if (!data) return [] as Array<{ date: string; files: string[] }>;
    const map = new Map<string, string[]>();
    for (const f of data) {
      const date = extractDate(f);
      const arr = map.get(date) ?? [];
      arr.push(f);
      map.set(date, arr);
    }
    return [...map.entries()]
      .sort((a, b) => (a[0] < b[0] ? 1 : -1))
      .map(([date, files]) => ({
        date,
        files: files.sort(),
      }));
  }, [data]);

  return (
    <Panel title="BATCH BROWSER" span={4}>
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
        <TextInput
          label="TAG"
          name="tag"
          id="batches-filter-tag"
          placeholder="—"
          value={pending.tag ?? ''}
          onChange={(e) => setPending({ ...pending, tag: e.target.value || undefined })}
          style={{ width: 100 }}
        />
        <TextInput
          label="EXT"
          name="extension"
          placeholder="—"
          value={pending.extension ?? ''}
          onChange={(e) =>
            setPending({ ...pending, extension: e.target.value || undefined })
          }
          style={{ width: 60 }}
        />
        <Button size="sm" onClick={() => setApplied(pending)}>
          APPLY
        </Button>
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
      {data && data.length === 0 && <div className="dim">— NO FILES —</div>}

      <div className="list">
        {grouped.map((g) => (
          <div key={g.date} className="tree-group">
            <div className="tree-group__header">{g.date}</div>
            {g.files.map((f) => {
              const ext = extractExtension(f);
              const isPng = ext === 'png';
              return (
                <div key={f} className="list-row" style={{ cursor: 'default' }}>
                  <span className="list-row__name" title={f}>├ {f}</span>
                  <span style={{ display: 'flex', gap: 4 }}>
                    {isPng && (
                      <Button size="sm" tone="dim" onClick={() => setPreview(f)}>
                        VIEW
                      </Button>
                    )}
                    <a
                      href={batchFileUrl(f)}
                      target="_blank"
                      rel="noreferrer"
                      download
                      className="btn btn--dim btn--sm"
                      style={{ textDecoration: 'none' }}
                    >
                      <span className="btn__bracket">[</span>
                      <span className="btn__label">DL</span>
                      <span className="btn__bracket">]</span>
                    </a>
                  </span>
                </div>
              );
            })}
          </div>
        ))}
      </div>

      {preview && <BatchLightbox fileName={preview} onClose={() => setPreview(null)} />}
    </Panel>
  );
}
