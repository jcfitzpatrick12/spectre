import { useMemo, useState } from 'react';
import { Panel } from '../components/Panel';
import { Readout } from '../components/Readout';
import { Button } from '../components/Button';
import { TextInput } from '../components/Field';
import { useConfigs } from '../api/queries';
import { useRecordings } from '../state/RecordingsContext';
import './RecordPanel.css';

type Kind = 'signal' | 'spectrogram';

function tagFromFileName(fileName: string): string {
  return fileName.endsWith('.json') ? fileName.slice(0, -5) : fileName;
}

export function RecordPanel() {
  const { data: configs } = useConfigs();
  const { start, inFlight, isRecordingAny } = useRecordings();
  const [selectedTags, setSelectedTags] = useState<Set<string>>(new Set());
  const [duration, setDuration] = useState('10');
  const [kind, setKind] = useState<Kind>('spectrogram');
  const [forceRestart, setForceRestart] = useState(false);
  const [maxRestarts, setMaxRestarts] = useState('0');
  const [validate, setValidate] = useState(true);

  const tags = useMemo(() => configs?.map(tagFromFileName) ?? [], [configs]);
  const selectedArr = useMemo(() => [...selectedTags], [selectedTags]);
  const durationNum = Number.parseInt(duration, 10);
  const maxNum = Number.parseInt(maxRestarts, 10);
  const durationOk = Number.isFinite(durationNum) && durationNum > 0;

  const conflict = isRecordingAny(selectedArr);
  const canSubmit = selectedArr.length > 0 && durationOk && !conflict;

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) => {
      const next = new Set(prev);
      if (next.has(tag)) next.delete(tag);
      else next.add(tag);
      return next;
    });
  };

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    start({
      kind,
      tags: selectedArr,
      duration: durationNum,
      force_restart: forceRestart,
      max_restarts: Number.isFinite(maxNum) ? maxNum : 0,
      validate,
    });
    // Reset transient inputs but keep selection so user can quickly re-fire.
  };

  return (
    <Panel
      title="REC"
      span={2}
      tone={inFlight.length ? 'accent' : 'default'}
      readout={
        <Readout
          rows={[
            {
              label: 'MODE',
              value: inFlight.length ? 'BUSY' : 'IDLE',
              tone: inFlight.length ? 'accent' : 'dim',
            },
            {
              label: 'JOBS',
              value: inFlight.length,
              tone: inFlight.length ? 'accent' : 'dim',
            },
          ]}
        />
      }
    >
      <form className="rec-form" onSubmit={submit}>
        <div className="rec-form__kind">
          {(['spectrogram', 'signal'] as Kind[]).map((k) => (
            <label
              key={k}
              className={`rec-form__radio ${kind === k ? 'rec-form__radio--active' : ''}`}
            >
              <input
                type="radio"
                name="kind"
                value={k}
                checked={kind === k}
                onChange={() => setKind(k)}
              />
              <span>{k === 'spectrogram' ? 'SPG' : 'SIG'}</span>
            </label>
          ))}
        </div>

        <TextInput
          label="DUR (s)"
          name="duration"
          id="rec-duration"
          inputMode="numeric"
          value={duration}
          onChange={(e) => setDuration(e.target.value)}
          required
        />

        <div className="rec-form__tags">
          <div className="rec-form__label">TAGS</div>
          {tags.length === 0 ? (
            <div className="dim" style={{ fontSize: 11 }}>— NO CONFIGS —</div>
          ) : (
            <div className="rec-form__tag-list">
              {tags.map((tag) => (
                <label
                  key={tag}
                  className={`rec-form__tag ${
                    selectedTags.has(tag) ? 'rec-form__tag--active' : ''
                  }`}
                  title={tag}
                >
                  <input
                    type="checkbox"
                    checked={selectedTags.has(tag)}
                    onChange={() => toggleTag(tag)}
                  />
                  <span>{tag}</span>
                </label>
              ))}
            </div>
          )}
        </div>

        <details className="rec-form__advanced">
          <summary>ADV</summary>
          <div className="rec-form__adv-inner">
            <label className="rec-form__toggle">
              <input
                type="checkbox"
                checked={forceRestart}
                onChange={(e) => setForceRestart(e.target.checked)}
              />
              <span>FORCE-RESTART</span>
            </label>
            <TextInput
              label="MAX-RESTARTS"
              name="max_restarts"
              inputMode="numeric"
              value={maxRestarts}
              onChange={(e) => setMaxRestarts(e.target.value)}
            />
            <label className="rec-form__toggle">
              <input
                type="checkbox"
                checked={validate}
                onChange={(e) => setValidate(e.target.checked)}
              />
              <span>VALIDATE</span>
            </label>
          </div>
        </details>

        {conflict && (
          <div className="err" style={{ fontSize: 11 }}>
            ALREADY IN FLIGHT
          </div>
        )}

        <Button type="submit" tone="accent" disabled={!canSubmit}>
          RUN
        </Button>

        <div className="rec-form__hint" title="Backend has no cancel/status endpoint (issue #192). Closing the tab orphans this view but the recording continues server-side.">
          NO CANCEL · SEE #192
        </div>
      </form>
    </Panel>
  );
}
