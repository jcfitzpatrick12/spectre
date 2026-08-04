import { useState } from 'react';
import { Panel } from '../components/Panel';
import { Button } from '../components/Button';
import { TextInput } from '../components/Field';
import { batchFileUrl, useBatchTags } from '../api/queries';
import { usePlotMutation } from '../api/plots';
import type { PlotResult } from '../api/plots';
import { SpectreApiError } from '../api/client';
import './list-common.css';
import './SpectrogramPanel.css';

interface FormState {
  tagsCsv: string;
  obs_date: string;
  start_time: string;
  end_time: string;
  lower_freq: string;
  upper_freq: string;
  log_norm: boolean;
  dBb: boolean;
  vmin: string;
  vmax: string;
  figsize_x: string;
  figsize_y: string;
}

const EMPTY: FormState = {
  tagsCsv: '',
  obs_date: '',
  start_time: '',
  end_time: '',
  lower_freq: '',
  upper_freq: '',
  log_norm: false,
  dBb: false,
  vmin: '',
  vmax: '',
  figsize_x: '',
  figsize_y: '',
};

function parseFloatOrNull(v: string): number | null {
  if (!v.trim()) return null;
  const n = Number.parseFloat(v);
  return Number.isFinite(n) ? n : null;
}

function parseIntOrNull(v: string): number | null {
  if (!v.trim()) return null;
  const n = Number.parseInt(v, 10);
  return Number.isFinite(n) ? n : null;
}

function parseTags(csv: string): string[] {
  return csv
    .split(',')
    .map((t) => t.trim())
    .filter(Boolean);
}

export function SpectrogramPanel() {
  const [form, setForm] = useState<FormState>(EMPTY);
  const [recent, setRecent] = useState<PlotResult[]>([]);
  const [active, setActive] = useState<PlotResult | null>(null);
  const { data: knownTags } = useBatchTags({});
  const mutation = usePlotMutation();

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const tags = parseTags(form.tagsCsv);
    if (tags.length === 0 || !form.obs_date || !form.start_time || !form.end_time) return;

    mutation.mutate(
      {
        tags,
        obs_date: form.obs_date,
        start_time: form.start_time,
        end_time: form.end_time,
        lower_freq: parseFloatOrNull(form.lower_freq),
        upper_freq: parseFloatOrNull(form.upper_freq),
        log_norm: form.log_norm,
        dBb: form.dBb,
        vmin: parseFloatOrNull(form.vmin),
        vmax: parseFloatOrNull(form.vmax),
        figsize_x: parseIntOrNull(form.figsize_x),
        figsize_y: parseIntOrNull(form.figsize_y),
      },
      {
        onSuccess: (result) => {
          setActive(result);
          setRecent((r) => [result, ...r.filter((p) => p.fileName !== result.fileName)].slice(0, 5));
        },
      },
    );
  };

  const errorMessage =
    mutation.error instanceof SpectreApiError
      ? mutation.error.message
      : mutation.error
        ? String(mutation.error)
        : null;

  return (
    <Panel title="SPECTROGRAM VIEWER" span={8}>
      <div className="plot-layout">
        <form className="plot-form" onSubmit={submit}>
          <TextInput
            label="TAGS (CSV)"
            name="tags"
            placeholder="sun,moon"
            value={form.tagsCsv}
            onChange={(e) => update('tagsCsv', e.target.value)}
            list="known-tags"
            required
          />
          {knownTags && (
            <datalist id="known-tags">
              {knownTags.map((t) => (
                <option key={t} value={t} />
              ))}
            </datalist>
          )}
          <TextInput
            label="OBS DATE"
            name="obs_date"
            type="date"
            value={form.obs_date}
            onChange={(e) => update('obs_date', e.target.value)}
            required
          />
          <TextInput
            label="START"
            name="start_time"
            type="time"
            step={1}
            value={form.start_time}
            onChange={(e) => update('start_time', e.target.value)}
            required
          />
          <TextInput
            label="END"
            name="end_time"
            type="time"
            step={1}
            value={form.end_time}
            onChange={(e) => update('end_time', e.target.value)}
            required
          />
          <TextInput
            label="LOWER Hz"
            name="lower_freq"
            inputMode="decimal"
            placeholder="—"
            value={form.lower_freq}
            onChange={(e) => update('lower_freq', e.target.value)}
          />
          <TextInput
            label="UPPER Hz"
            name="upper_freq"
            inputMode="decimal"
            placeholder="—"
            value={form.upper_freq}
            onChange={(e) => update('upper_freq', e.target.value)}
          />
          <TextInput
            label="VMIN"
            name="vmin"
            inputMode="decimal"
            placeholder="—"
            value={form.vmin}
            onChange={(e) => update('vmin', e.target.value)}
          />
          <TextInput
            label="VMAX"
            name="vmax"
            inputMode="decimal"
            placeholder="—"
            value={form.vmax}
            onChange={(e) => update('vmax', e.target.value)}
          />
          <TextInput
            label="FIG X"
            name="figsize_x"
            inputMode="numeric"
            placeholder="15"
            value={form.figsize_x}
            onChange={(e) => update('figsize_x', e.target.value)}
          />
          <TextInput
            label="FIG Y"
            name="figsize_y"
            inputMode="numeric"
            placeholder="8"
            value={form.figsize_y}
            onChange={(e) => update('figsize_y', e.target.value)}
          />
          <label className="plot-form__toggle">
            <input
              type="checkbox"
              checked={form.log_norm}
              onChange={(e) => update('log_norm', e.target.checked)}
            />
            <span>LOG-NORM</span>
          </label>
          <label className="plot-form__toggle">
            <input
              type="checkbox"
              checked={form.dBb}
              onChange={(e) => update('dBb', e.target.checked)}
            />
            <span>dBb</span>
          </label>
          <div className="plot-form__actions">
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? 'PLOTTING…' : 'PLOT'}
            </Button>
            <Button type="button" tone="dim" onClick={() => setForm(EMPTY)}>
              CLEAR
            </Button>
          </div>
        </form>

        <div className="plot-preview">
          {errorMessage && <div className="err">FAIL — {errorMessage}</div>}
          {!active && !mutation.isPending && !errorMessage && (
            <div className="dim">— NO PLOT —</div>
          )}
          {mutation.isPending && <div className="dim">GENERATING…</div>}
          {active && (
            <div className="plot-preview__image">
              <img
                src={batchFileUrl(active.fileName)}
                alt={active.fileName}
              />
              <div className="plot-preview__caption">{active.fileName}</div>
            </div>
          )}
          {recent.length > 0 && (
            <div className="plot-recent">
              <div className="plot-recent__label">RECENT</div>
              <div className="plot-recent__row">
                {recent.map((r) => (
                  <button
                    key={r.fileName}
                    type="button"
                    className={`plot-recent__thumb ${
                      active?.fileName === r.fileName ? 'plot-recent__thumb--active' : ''
                    }`}
                    onClick={() => setActive(r)}
                    title={r.fileName}
                  >
                    <img src={batchFileUrl(r.fileName)} alt="" />
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </Panel>
  );
}
