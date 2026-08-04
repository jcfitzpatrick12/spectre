import { useState } from 'react';
import { Panel } from '../components/Panel';
import { Modal } from '../components/Modal';
import { JsonView } from '../components/JsonView';
import { Button } from '../components/Button';
import {
  useReceivers,
  useReceiverConnected,
  useReceiverModes,
  useReceiverModel,
} from '../api/queries';
import './list-common.css';

function ReceiverRow({
  name,
  selected,
  onSelect,
}: {
  name: string;
  selected: boolean;
  onSelect: () => void;
}) {
  const { data, isLoading } = useReceiverConnected(name);
  const status = isLoading ? '....' : data ? 'CONN' : '----';
  const tone = isLoading ? 'dim' : data ? 'default' : 'dim';
  return (
    <button
      type="button"
      className={`list-row ${selected ? 'list-row--selected' : ''}`}
      onClick={onSelect}
    >
      <span className="list-row__name">{name}</span>
      <span className={`list-row__badge list-row__badge--${tone}`}>[{status}]</span>
    </button>
  );
}

function ReceiverModelViewer({
  name,
  onClose,
}: {
  name: string;
  onClose: () => void;
}) {
  const { data: modes, isLoading, error } = useReceiverModes(name);
  const [mode, setMode] = useState<string | null>(null);
  const { data: model, isLoading: modelLoading, error: modelError } = useReceiverModel(
    name,
    mode ?? undefined,
  );

  return (
    <Modal title={`RECEIVER · ${name}`} onClose={onClose} wide>
      {isLoading && <div className="dim">LOADING MODES…</div>}
      {error && <div className="err">FAIL — {String(error)}</div>}
      {modes && (
        <div className="stack">
          <div className="row-wrap">
            <span className="dim">MODE:</span>
            {modes.length === 0 && <span className="dim">— NONE —</span>}
            {modes.map((m) => (
              <Button
                key={m}
                size="sm"
                tone={m === mode ? 'default' : 'dim'}
                onClick={() => setMode(m)}
              >
                {m}
              </Button>
            ))}
          </div>
          {mode && (
            <div className="stack">
              <div className="dim">SCHEMA · {mode}</div>
              {modelLoading && <div className="dim">LOADING SCHEMA…</div>}
              {modelError && <div className="err">FAIL — {String(modelError)}</div>}
              {model && <JsonView value={model} />}
            </div>
          )}
        </div>
      )}
    </Modal>
  );
}

export function ReceiversPanel() {
  const { data, isLoading, error } = useReceivers();
  const [openName, setOpenName] = useState<string | null>(null);

  return (
    <Panel title="RECEIVERS" span={4}>
      {isLoading && <div className="dim">SCANNING…</div>}
      {error && <div className="err">FAIL — {String(error)}</div>}
      {data && data.length === 0 && <div className="dim">— NONE —</div>}
      {data && (
        <div className="list">
          {data.map((name) => (
            <ReceiverRow
              key={name}
              name={name}
              selected={openName === name}
              onSelect={() => setOpenName(name)}
            />
          ))}
        </div>
      )}
      {openName && (
        <ReceiverModelViewer name={openName} onClose={() => setOpenName(null)} />
      )}
    </Panel>
  );
}
