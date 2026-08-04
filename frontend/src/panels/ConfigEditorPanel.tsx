import { useEffect, useMemo, useState } from 'react';
import { Panel } from '../components/Panel';
import { Modal } from '../components/Modal';
import { Button } from '../components/Button';
import { TextInput, Select } from '../components/Field';
import {
  useConfigRaw,
  useReceivers,
  useReceiverModes,
  useReceiverModel,
} from '../api/queries';
import { useCreateConfig, useUpdateConfig, useDeleteConfig } from '../api/configs';
import { SpectreApiError } from '../api/client';
import './list-common.css';
import './ConfigEditorPanel.css';

type Mode = 'idle' | 'create' | 'edit';

interface FieldSpec {
  name: string;
  type: 'string' | 'number' | 'integer' | 'boolean' | 'unknown';
  description?: string;
  default?: unknown;
  required: boolean;
}

/**
 * Very small subset of Pydantic-generated JSON schema we care about.
 * Only the shape needed to render a first-cut form.
 */
interface RawSchema {
  properties?: Record<string, Record<string, unknown>>;
  required?: string[];
}

function classifyType(prop: Record<string, unknown>): FieldSpec['type'] {
  const t = prop.type;
  if (t === 'boolean') return 'boolean';
  if (t === 'integer') return 'integer';
  if (t === 'number') return 'number';
  if (t === 'string') return 'string';
  if (Array.isArray(prop.anyOf)) {
    // e.g. [{type:'number'}, {type:'null'}]
    const first = prop.anyOf.find((v) => (v as Record<string, unknown>).type !== 'null') as
      | Record<string, unknown>
      | undefined;
    if (first) return classifyType(first);
  }
  return 'unknown';
}

function extractFields(schema: RawSchema | undefined): FieldSpec[] {
  if (!schema?.properties) return [];
  const required = new Set(schema.required ?? []);
  return Object.entries(schema.properties).map(([name, prop]) => ({
    name,
    type: classifyType(prop),
    description: typeof prop.description === 'string' ? prop.description : undefined,
    default: prop.default,
    required: required.has(name),
  }));
}

function toString(v: unknown): string {
  if (v === undefined || v === null) return '';
  if (typeof v === 'boolean') return v ? 'true' : 'false';
  return String(v);
}

function serialiseParams(values: Record<string, string>, fields: FieldSpec[]): string[] {
  const out: string[] = [];
  for (const f of fields) {
    const raw = values[f.name] ?? '';
    if (!raw.trim()) continue;
    out.push(`${f.name}=${raw}`);
  }
  return out;
}

/** Diff two value maps and return only the keys that changed for a PATCH. */
function diffParams(
  values: Record<string, string>,
  baseline: Record<string, string>,
  fields: FieldSpec[],
): string[] {
  const out: string[] = [];
  for (const f of fields) {
    const current = values[f.name] ?? '';
    const before = baseline[f.name] ?? '';
    if (current === before) continue;
    if (!current.trim()) continue; // don't blank fields via patch
    out.push(`${f.name}=${current}`);
  }
  return out;
}

interface ConfirmDeleteProps {
  fileName: string;
  onCancel: () => void;
  onConfirmed: () => void;
}

function ConfirmDelete({ fileName, onCancel, onConfirmed }: ConfirmDeleteProps) {
  const del = useDeleteConfig();
  const [previewed, setPreviewed] = useState(false);

  const runDryRun = () =>
    del.mutate(
      { fileName, dry_run: true },
      {
        onSuccess: () => setPreviewed(true),
      },
    );

  const runReal = () =>
    del.mutate(
      { fileName, dry_run: false },
      {
        onSuccess: () => onConfirmed(),
      },
    );

  const err =
    del.error instanceof SpectreApiError ? del.error.message : del.error ? String(del.error) : null;

  return (
    <Modal title={`DELETE · ${fileName}`} onClose={onCancel}>
      <div className="stack">
        <div className="dim">This will permanently delete the config file.</div>
        {err && <div className="err">FAIL — {err}</div>}
        {!previewed ? (
          <div className="row-wrap">
            <Button tone="dim" onClick={runDryRun} disabled={del.isPending}>
              {del.isPending ? 'CHECKING…' : 'PREVIEW (DRY-RUN)'}
            </Button>
            <Button tone="dim" onClick={onCancel}>CANCEL</Button>
          </div>
        ) : (
          <div className="row-wrap">
            <Button tone="accent" onClick={runReal} disabled={del.isPending}>
              {del.isPending ? 'DELETING…' : 'CONFIRM DELETE'}
            </Button>
            <Button tone="dim" onClick={onCancel}>CANCEL</Button>
          </div>
        )}
      </div>
    </Modal>
  );
}

interface CopyDialogProps {
  sourceFileName: string;
  sourceRaw: {
    receiver_name: string;
    receiver_mode: string;
    parameters: Record<string, unknown>;
  };
  onCancel: () => void;
  onCopied: (newFileName: string) => void;
}

function CopyDialog({ sourceFileName, sourceRaw, onCancel, onCopied }: CopyDialogProps) {
  const [newTag, setNewTag] = useState('');
  const create = useCreateConfig();
  const err =
    create.error instanceof SpectreApiError
      ? create.error.message
      : create.error
        ? String(create.error)
        : null;

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const tag = newTag.trim();
    if (!tag) return;
    const fileName = tag.endsWith('.json') ? tag : `${tag}.json`;
    const string_parameters = Object.entries(sourceRaw.parameters).map(
      ([k, v]) => `${k}=${toString(v)}`,
    );
    create.mutate(
      {
        fileName,
        receiver_name: sourceRaw.receiver_name,
        receiver_mode: sourceRaw.receiver_mode,
        string_parameters,
      },
      {
        onSuccess: () => onCopied(fileName),
      },
    );
  };

  return (
    <Modal title={`COPY · ${sourceFileName}`} onClose={onCancel}>
      <form className="stack" onSubmit={submit}>
        <div className="dim">Copy this config under a new tag.</div>
        <TextInput
          label="NEW TAG"
          name="newTag"
          placeholder="my_tag"
          value={newTag}
          onChange={(e) => setNewTag(e.target.value)}
          required
          autoFocus
        />
        {err && <div className="err">FAIL — {err}</div>}
        <div className="row-wrap">
          <Button type="submit" disabled={create.isPending}>
            {create.isPending ? 'COPYING…' : 'COPY'}
          </Button>
          <Button type="button" tone="dim" onClick={onCancel}>CANCEL</Button>
        </div>
      </form>
    </Modal>
  );
}

export function ConfigEditorPanel({
  selectedFileName,
  onSelectFileName,
}: {
  selectedFileName: string | null;
  onSelectFileName: (fileName: string | null) => void;
}) {
  const { data: receivers } = useReceivers();
  const [mode, setMode] = useState<Mode>('idle');
  const [tag, setTag] = useState('');
  const [receiver, setReceiver] = useState('');
  const [receiverMode, setReceiverMode] = useState('');
  const [values, setValues] = useState<Record<string, string>>({});
  const [baselineValues, setBaselineValues] = useState<Record<string, string>>({});
  const [force, setForce] = useState(false);
  const [validate, setValidate] = useState(true);
  const [showCopy, setShowCopy] = useState(false);
  const [showDelete, setShowDelete] = useState(false);

  const { data: modes } = useReceiverModes(receiver || undefined);
  const { data: schema } = useReceiverModel(
    receiver || undefined,
    receiverMode || undefined,
  );
  const { data: rawConfig } = useConfigRaw(
    mode === 'edit' && selectedFileName ? selectedFileName : undefined,
  );

  const fields = useMemo(() => extractFields(schema as RawSchema | undefined), [schema]);
  const create = useCreateConfig();
  const update = useUpdateConfig();

  // When a config is selected externally, hydrate the editor for edit mode.
  // If the user was mid-create, switch to edit; hydration is driven by the
  // rawConfig effect below. If selection is cleared and we were editing,
  // fall back to idle and drop the form.
  useEffect(() => {
    if (selectedFileName && mode !== 'edit') {
      setMode('edit');
    } else if (!selectedFileName && mode === 'edit') {
      setMode('idle');
      setReceiver('');
      setReceiverMode('');
      setValues({});
      setBaselineValues({});
    }
  }, [selectedFileName, mode]);

  useEffect(() => {
    if (mode === 'edit' && rawConfig) {
      setReceiver(rawConfig.receiver_name);
      setReceiverMode(rawConfig.receiver_mode);
      const stringified: Record<string, string> = {};
      for (const [k, v] of Object.entries(rawConfig.parameters)) {
        stringified[k] = toString(v);
      }
      setValues(stringified);
      setBaselineValues(stringified);
    }
  }, [mode, rawConfig]);

  // In create mode, seed the parameter values from schema defaults when
  // the schema arrives.
  useEffect(() => {
    if (mode === 'create' && fields.length) {
      setValues((prev) => {
        const next = { ...prev };
        for (const f of fields) {
          if (next[f.name] === undefined && f.default !== undefined) {
            next[f.name] = toString(f.default);
          }
        }
        return next;
      });
    }
  }, [mode, fields]);

  const beginCreate = () => {
    onSelectFileName(null);
    setMode('create');
    setTag('');
    setReceiver('');
    setReceiverMode('');
    setValues({});
    setBaselineValues({});
    setForce(false);
    setValidate(true);
  };

  const cancel = () => {
    onSelectFileName(null);
    setMode('idle');
    setTag('');
    setReceiver('');
    setReceiverMode('');
    setValues({});
    setBaselineValues({});
  };

  const canSave =
    (mode === 'create' && tag.trim() && receiver && receiverMode) ||
    (mode === 'edit' && !!selectedFileName);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSave) return;
    if (mode === 'create') {
      const fileName = tag.trim().endsWith('.json')
        ? tag.trim()
        : `${tag.trim()}.json`;
      create.mutate(
        {
          fileName,
          receiver_name: receiver,
          receiver_mode: receiverMode,
          string_parameters: serialiseParams(values, fields),
          force,
          validate,
        },
        {
          onSuccess: () => {
            onSelectFileName(fileName);
            setMode('edit');
            setBaselineValues(values);
          },
        },
      );
    } else if (mode === 'edit' && selectedFileName) {
      const params = diffParams(values, baselineValues, fields);
      if (params.length === 0) return;
      update.mutate(
        {
          fileName: selectedFileName,
          params,
          force,
          validate,
        },
        {
          onSuccess: () => setBaselineValues(values),
        },
      );
    }
  };

  const mutation = mode === 'create' ? create : update;
  const err =
    mutation.error instanceof SpectreApiError
      ? mutation.error.message
      : mutation.error
        ? String(mutation.error)
        : null;

  return (
    <Panel
      title="CONFIG EDITOR"
      span={6}
      tone={mode === 'idle' ? 'dim' : 'default'}
      actions={
        mode === 'idle' ? (
          <Button size="sm" onClick={beginCreate} id="cfg-new">NEW</Button>
        ) : (
          <Button size="sm" tone="dim" onClick={cancel}>CANCEL</Button>
        )
      }
    >
      {mode === 'idle' && (
        <div className="dim">
          — SELECT A CONFIG ABOVE OR PRESS <span style={{ color: 'var(--fg)' }}>[NEW]</span> —
        </div>
      )}

      {mode !== 'idle' && (
        <form className="cfg-form" onSubmit={submit}>
          <div className="cfg-form__meta">
            {mode === 'create' ? (
              <TextInput
                label="TAG"
                name="tag"
                placeholder="my_tag"
                value={tag}
                onChange={(e) => setTag(e.target.value)}
                required
              />
            ) : (
              <div className="cfg-form__file">
                <div className="cfg-form__file-label">FILE</div>
                <div>{selectedFileName}</div>
              </div>
            )}

            <Select
              label="RECEIVER"
              name="receiver_name"
              value={receiver}
              onChange={(e) => {
                setReceiver(e.target.value);
                setReceiverMode('');
              }}
              disabled={mode === 'edit'}
              required
            >
              <option value="">—</option>
              {receivers?.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </Select>

            <Select
              label="MODE"
              name="receiver_mode"
              value={receiverMode}
              onChange={(e) => setReceiverMode(e.target.value)}
              disabled={mode === 'edit' || !receiver}
              required
            >
              <option value="">—</option>
              {modes?.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </Select>

            <div className="cfg-form__toggles">
              <label className="cfg-form__toggle">
                <input
                  type="checkbox"
                  checked={validate}
                  onChange={(e) => setValidate(e.target.checked)}
                />
                <span>VALIDATE</span>
              </label>
              <label className="cfg-form__toggle">
                <input
                  type="checkbox"
                  checked={force}
                  onChange={(e) => setForce(e.target.checked)}
                />
                <span>FORCE</span>
              </label>
            </div>
          </div>

          {fields.length > 0 ? (
            <div className="cfg-form__params">
              {fields.map((f) => (
                <TextInput
                  key={f.name}
                  label={
                    <span title={f.description ?? ''}>
                      {f.name}{f.required ? ' *' : ''}
                      {f.type !== 'unknown' && (
                        <span style={{ opacity: 0.5 }}> · {f.type}</span>
                      )}
                    </span>
                  }
                  name={f.name}
                  value={values[f.name] ?? ''}
                  onChange={(e) => setValues({ ...values, [f.name]: e.target.value })}
                  placeholder={f.default !== undefined ? toString(f.default) : '—'}
                />
              ))}
            </div>
          ) : (
            <div className="dim">
              {receiver && receiverMode
                ? '— LOADING SCHEMA —'
                : '— PICK A RECEIVER AND MODE —'}
            </div>
          )}

          {err && <div className="err">FAIL — {err}</div>}

          <div className="cfg-form__actions">
            <Button type="submit" disabled={!canSave || mutation.isPending}>
              {mutation.isPending ? 'SAVING…' : mode === 'create' ? 'CREATE' : 'UPDATE'}
            </Button>
            {mode === 'edit' && (
              <>
                <Button
                  type="button"
                  tone="dim"
                  onClick={() => setShowCopy(true)}
                  disabled={!rawConfig}
                >
                  COPY
                </Button>
                <Button
                  type="button"
                  tone="accent"
                  onClick={() => setShowDelete(true)}
                >
                  DELETE
                </Button>
              </>
            )}
          </div>
        </form>
      )}

      {showCopy && rawConfig && selectedFileName && (
        <CopyDialog
          sourceFileName={selectedFileName}
          sourceRaw={rawConfig}
          onCancel={() => setShowCopy(false)}
          onCopied={(newFileName) => {
            setShowCopy(false);
            onSelectFileName(newFileName);
          }}
        />
      )}

      {showDelete && selectedFileName && (
        <ConfirmDelete
          fileName={selectedFileName}
          onCancel={() => setShowDelete(false)}
          onConfirmed={() => {
            setShowDelete(false);
            cancel();
          }}
        />
      )}
    </Panel>
  );
}
