import { Panel } from '../components/Panel';
import { useConfigs } from '../api/queries';
import './list-common.css';

export interface ConfigsPanelProps {
  selectedFileName: string | null;
  onSelect: (fileName: string) => void;
}

export function ConfigsPanel({ selectedFileName, onSelect }: ConfigsPanelProps) {
  const { data, isLoading, error } = useConfigs();

  return (
    <Panel title="CONFIGS" span={2}>
      {isLoading && <div className="dim">LOADING…</div>}
      {error && <div className="err">FAIL — {String(error)}</div>}
      {data && data.length === 0 && <div className="dim">— NONE —</div>}
      {data && (
        <div className="list">
          {data.map((name) => (
            <button
              key={name}
              type="button"
              className={`list-row ${selectedFileName === name ? 'list-row--selected' : ''}`}
              onClick={() => onSelect(name)}
              title={name}
            >
              <span className="list-row__name">{name}</span>
            </button>
          ))}
        </div>
      )}
    </Panel>
  );
}
