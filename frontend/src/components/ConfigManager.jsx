import React, { useState, useEffect } from 'react'
import { apiClient } from '../services/apiClient'

function ConfigManager({ onConfigsChange }) {
  const [configs, setConfigs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [refreshing, setRefreshing] = useState(false)

  // Modal states
  const [viewingConfig, setViewingConfig] = useState(null)
  const [editingConfig, setEditingConfig] = useState(null)
  const [deletingConfig, setDeletingConfig] = useState(null)
  const [creatingConfig, setCreatingConfig] = useState(false)

  // Form states
  const [editedJson, setEditedJson] = useState('')
  const [jsonError, setJsonError] = useState(null)
  const [saving, setSaving] = useState(false)

  // Create form states
  const [newConfigName, setNewConfigName] = useState('')
  const [receivers, setReceivers] = useState([])
  const [selectedReceiver, setSelectedReceiver] = useState('')
  const [receiverModes, setReceiverModes] = useState([])
  const [selectedMode, setSelectedMode] = useState('')
  const [templateParams, setTemplateParams] = useState('')

  useEffect(() => {
    loadConfigs()
  }, [])

  const loadConfigs = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await apiClient.getConfigs()
      const configUrls = response.data || []

      // Extract filenames from URLs
      const configFiles = configUrls.map(url => {
        const parts = url.split('/')
        return parts[parts.length - 1]
      })

      // Load config details for each
      const configDetails = await Promise.all(
        configFiles.map(async (fileName) => {
          try {
            const rawResponse = await apiClient.getConfigRaw(fileName)
            return {
              fileName,
              tag: fileName.replace('.json', ''),
              ...rawResponse.data
            }
          } catch (err) {
            console.error(`Failed to load ${fileName}:`, err)
            return {
              fileName,
              tag: fileName.replace('.json', ''),
              error: err.message
            }
          }
        })
      )

      setConfigs(configDetails)
    } catch (err) {
      setError(`Failed to load configs: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    try {
      setRefreshing(true)
      setError(null)
      await loadConfigs()
    } catch (err) {
      setError(`Failed to refresh configs: ${err.message}`)
    } finally {
      setRefreshing(false)
    }
  }

  const handleView = async (config) => {
    setViewingConfig(config)
  }

  const handleEdit = async (config) => {
    setEditingConfig(config)
    setEditedJson(JSON.stringify(config.parameters, null, 2))
    setJsonError(null)
  }

  const handleSaveEdit = async () => {
    try {
      setJsonError(null)

      // Validate JSON
      let parsedParams
      try {
        parsedParams = JSON.parse(editedJson)
      } catch (err) {
        setJsonError(`Invalid JSON: ${err.message}`)
        return
      }

      // Convert parameters to string_parameters format
      const stringParams = Object.entries(parsedParams).map(
        ([key, value]) => `${key}=${value}`
      )

      setSaving(true)
      await apiClient.updateConfig(editingConfig.fileName, {
        params: stringParams,
        validate: true,
        force: false
      })

      // Reload configs and close editor
      await loadConfigs()
      setEditingConfig(null)
      setEditedJson('')

      // Notify parent component
      if (onConfigsChange) {
        onConfigsChange()
      }
    } catch (err) {
      setJsonError(`Save failed: ${err.message}`)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (config) => {
    setDeletingConfig(config)
  }

  const confirmDelete = async () => {
    try {
      setSaving(true)
      setError(null)

      await apiClient.deleteConfig(deletingConfig.fileName, false)

      // Reload configs and close dialog
      await loadConfigs()
      setDeletingConfig(null)

      // Notify parent component
      if (onConfigsChange) {
        onConfigsChange()
      }
    } catch (err) {
      setError(`Delete failed: ${err.message}`)
      setDeletingConfig(null)
    } finally {
      setSaving(false)
    }
  }

  const handleCreateNew = async () => {
    try {
      setCreatingConfig(true)

      // Load receivers for create form
      const receiversResponse = await apiClient.getReceivers()
      setReceivers(receiversResponse.data || [])

      setNewConfigName('')
      setSelectedReceiver('')
      setReceiverModes([])
      setSelectedMode('')
      setTemplateParams('')
      setJsonError(null)
    } catch (err) {
      setError(`Failed to load receivers: ${err.message}`)
      setCreatingConfig(false)
    }
  }

  const handleReceiverChange = async (receiverName) => {
    try {
      setSelectedReceiver(receiverName)
      setSelectedMode('')
      setTemplateParams('')

      // Load modes for selected receiver
      const modesResponse = await apiClient.getReceiverModes(receiverName)
      setReceiverModes(modesResponse.data || [])
    } catch (err) {
      setJsonError(`Failed to load modes: ${err.message}`)
    }
  }

  const handleLoadTemplate = async () => {
    try {
      if (!selectedReceiver || !selectedMode) {
        setJsonError('Please select both receiver and mode')
        return
      }

      setJsonError(null)
      const modelResponse = await apiClient.getReceiverModel(selectedReceiver, selectedMode)
      setTemplateParams(JSON.stringify(modelResponse.data, null, 2))
    } catch (err) {
      setJsonError(`Failed to load template: ${err.message}`)
    }
  }

  const handleCreateConfig = async () => {
    try {
      setJsonError(null)

      // Validate inputs
      if (!newConfigName.trim()) {
        setJsonError('Config name is required')
        return
      }

      if (!selectedReceiver || !selectedMode) {
        setJsonError('Please select receiver and mode')
        return
      }

      // Parse parameters if provided
      let stringParams = []
      if (templateParams.trim()) {
        try {
          const parsedParams = JSON.parse(templateParams)
          stringParams = Object.entries(parsedParams).map(
            ([key, value]) => `${key}=${value}`
          )
        } catch (err) {
          setJsonError(`Invalid JSON parameters: ${err.message}`)
          return
        }
      }

      setSaving(true)

      const fileName = `${newConfigName.trim()}.json`
      await apiClient.createConfig(fileName, {
        receiver_name: selectedReceiver,
        receiver_mode: selectedMode,
        string_parameters: stringParams,
        validate: true,
        force: false
      })

      // Reload configs and close create form
      await loadConfigs()
      setCreatingConfig(false)

      // Notify parent component
      if (onConfigsChange) {
        onConfigsChange()
      }
    } catch (err) {
      setJsonError(`Create failed: ${err.message}`)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <>
        <h3>Configurations</h3>
        <div className="loading">Loading configurations...</div>
      </>
    )
  }

  return (
    <>
      <div className="gallery-header">
        <h3>Configurations</h3>
        <div className="gallery-controls">
          <button
            className="start-button"
            onClick={handleCreateNew}
            title="Create new configuration"
          >
            + Create New
          </button>
          <button
            className="refresh-button"
            onClick={handleRefresh}
            disabled={refreshing}
            title="Refresh configurations list"
          >
            {refreshing ? '↻ Refreshing...' : '↻ Refresh'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error">
          <p>{error}</p>
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      {configs.length === 0 ? (
        <p className="no-recordings">No configurations yet. Create your first one!</p>
      ) : (
        <div className="config-list">
          {configs.map((config) => (
            <div key={config.fileName} className="config-card">
              <div className="config-info">
                <p className="config-tag">
                  <strong>{config.tag}</strong>
                </p>
                <p className="config-details">
                  {config.receiver_name} - {config.receiver_mode}
                </p>
                {config.error && (
                  <p className="error-message">{config.error}</p>
                )}
              </div>
              <div className="config-actions">
                <button
                  className="config-action-button view"
                  onClick={() => handleView(config)}
                  title="View configuration"
                >
                  View
                </button>
                <button
                  className="config-action-button edit"
                  onClick={() => handleEdit(config)}
                  title="Edit configuration"
                >
                  Edit
                </button>
                <button
                  className="config-action-button delete"
                  onClick={() => handleDelete(config)}
                  title="Delete configuration"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* View Modal */}
      {viewingConfig && (
        <div className="config-modal" onClick={() => setViewingConfig(null)}>
          <div className="config-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="config-modal-header">
              <h3>View Configuration: {viewingConfig.tag}</h3>
              <button className="modal-close" onClick={() => setViewingConfig(null)}>×</button>
            </div>
            <div className="config-modal-body">
              <textarea
                className="json-editor"
                value={JSON.stringify(viewingConfig.parameters, null, 2)}
                readOnly
              />
            </div>
            <div className="config-modal-footer">
              <button className="start-button" onClick={() => {
                setViewingConfig(null)
                handleEdit(viewingConfig)
              }}>
                Edit
              </button>
              <button className="reset-button" onClick={() => setViewingConfig(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {editingConfig && (
        <div className="config-modal" onClick={() => !saving && setEditingConfig(null)}>
          <div className="config-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="config-modal-header">
              <h3>Edit Configuration: {editingConfig.tag}</h3>
              <button
                className="modal-close"
                onClick={() => !saving && setEditingConfig(null)}
                disabled={saving}
              >×</button>
            </div>
            <div className="config-modal-body">
              <textarea
                className="json-editor"
                value={editedJson}
                onChange={(e) => setEditedJson(e.target.value)}
                disabled={saving}
              />
              {jsonError && (
                <div className="error-message">{jsonError}</div>
              )}
            </div>
            <div className="config-modal-footer">
              <button
                className="start-button"
                onClick={handleSaveEdit}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
              <button
                className="reset-button"
                onClick={() => setEditingConfig(null)}
                disabled={saving}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deletingConfig && (
        <div className="config-modal" onClick={() => !saving && setDeletingConfig(null)}>
          <div className="config-modal-content small" onClick={(e) => e.stopPropagation()}>
            <div className="config-modal-header">
              <h3>Confirm Delete</h3>
              <button
                className="modal-close"
                onClick={() => !saving && setDeletingConfig(null)}
                disabled={saving}
              >×</button>
            </div>
            <div className="config-modal-body">
              <p>Are you sure you want to delete <strong>{deletingConfig.tag}</strong>?</p>
              <p className="warning-text">This action cannot be undone.</p>
            </div>
            <div className="config-modal-footer">
              <button
                className="delete-confirm-button"
                onClick={confirmDelete}
                disabled={saving}
              >
                {saving ? 'Deleting...' : 'Delete'}
              </button>
              <button
                className="reset-button"
                onClick={() => setDeletingConfig(null)}
                disabled={saving}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Modal */}
      {creatingConfig && (
        <div className="config-modal" onClick={() => !saving && setCreatingConfig(false)}>
          <div className="config-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="config-modal-header">
              <h3>Create New Configuration</h3>
              <button
                className="modal-close"
                onClick={() => !saving && setCreatingConfig(false)}
                disabled={saving}
              >×</button>
            </div>
            <div className="config-modal-body">
              <div className="form-group">
                <label htmlFor="config-name">Configuration Name (tag)</label>
                <input
                  id="config-name"
                  type="text"
                  value={newConfigName}
                  onChange={(e) => setNewConfigName(e.target.value)}
                  placeholder="my-config"
                  disabled={saving}
                />
              </div>

              <div className="form-group">
                <label htmlFor="receiver">Receiver</label>
                <select
                  id="receiver"
                  value={selectedReceiver}
                  onChange={(e) => handleReceiverChange(e.target.value)}
                  disabled={saving}
                >
                  <option value="">Select a receiver...</option>
                  {receivers.map(receiver => (
                    <option key={receiver} value={receiver}>{receiver}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="mode">Mode</label>
                <select
                  id="mode"
                  value={selectedMode}
                  onChange={(e) => setSelectedMode(e.target.value)}
                  disabled={saving || !selectedReceiver}
                >
                  <option value="">Select a mode...</option>
                  {receiverModes.map(mode => (
                    <option key={mode} value={mode}>{mode}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                  <label htmlFor="params">Parameters (JSON)</label>
                  <button
                    className="refresh-button"
                    onClick={handleLoadTemplate}
                    disabled={saving || !selectedReceiver || !selectedMode}
                    style={{padding: '0.25rem 0.75rem', fontSize: '0.85rem'}}
                  >
                    Load Template
                  </button>
                </div>
                <textarea
                  id="params"
                  className="json-editor"
                  value={templateParams}
                  onChange={(e) => setTemplateParams(e.target.value)}
                  placeholder='{"key": "value"}'
                  disabled={saving}
                  style={{minHeight: '200px'}}
                />
              </div>

              {jsonError && (
                <div className="error-message">{jsonError}</div>
              )}
            </div>
            <div className="config-modal-footer">
              <button
                className="start-button"
                onClick={handleCreateConfig}
                disabled={saving}
              >
                {saving ? 'Creating...' : 'Create'}
              </button>
              <button
                className="reset-button"
                onClick={() => setCreatingConfig(false)}
                disabled={saving}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default ConfigManager
