import React, { useEffect, useMemo, useState } from 'react'
import { apiClient } from '../services/apiClient'

const STATUS = {
  IDLE: 'idle',
  RECORDING: 'recording',
  PLOTTING: 'plotting',
  COMPLETE: 'complete',
  ERROR: 'error'
}

const STORAGE_KEY_TAG = 'spectre.selectedTag'

const INITIAL_FORM = {
  tag: '',
  duration: 30,
  forceRestart: false,
  maxRestarts: 5,
  validate: true
}

const clampNumber = (value) => (Number.isFinite(value) ? value : 0)

const getObservationWindow = (durationSeconds) => {
  const now = new Date()
  const start = new Date(now.getTime() - durationSeconds * 1000)
  const [startDate, startTimeRaw] = start.toISOString().split('T')
  const [endDate, endTimeRaw] = now.toISOString().split('T')

  return {
    obs_date: startDate,
    start_time: startTimeRaw.split('.')[0],
    end_time: endTimeRaw.split('.')[0],
    start_iso: start.toISOString(),
    end_iso: now.toISOString()
  }
}

function RecordingForm({ configs, onRecordingComplete }) {
  const [formData, setFormData] = useState(() => {
    const savedTag = localStorage.getItem(STORAGE_KEY_TAG)
    return {
      ...INITIAL_FORM,
      tag: savedTag || INITIAL_FORM.tag
    }
  })
  const [errors, setErrors] = useState({})
  const [status, setStatus] = useState(STATUS.IDLE)
  const [statusMessage, setStatusMessage] = useState('')
  const [resultImage, setResultImage] = useState(null)
  const [resultMeta, setResultMeta] = useState(null)

  const availableTags = useMemo(() => {
    if (!Array.isArray(configs) || configs.length === 0) return []
    return configs
      .map((configUrl) => configUrl?.split('/')?.pop() ?? '')
      .filter(Boolean)
      .map((fileName) => fileName.replace(/\.json$/i, ''))
      .sort()
  }, [configs])

  // Validate persisted tag exists in current configs
  useEffect(() => {
    if (formData.tag && availableTags.length > 0 && !availableTags.includes(formData.tag)) {
      // Stored tag no longer exists, clear it
      localStorage.removeItem(STORAGE_KEY_TAG)
      setFormData((prev) => ({ ...prev, tag: '' }))
    }
  }, [availableTags, formData.tag])

  const handleChange = (event) => {
    const { name, type, value, checked } = event.target

    setFormData((prev) => {
      if (type === 'checkbox') {
        return { ...prev, [name]: checked }
      }

      if (name === 'duration') {
        return { ...prev, duration: clampNumber(parseFloat(value)) }
      }

      if (name === 'maxRestarts') {
        return { ...prev, maxRestarts: clampNumber(parseInt(value, 10)) }
      }

      return { ...prev, [name]: value }
    })

    // Persist tag selection to localStorage
    if (name === 'tag') {
      localStorage.setItem(STORAGE_KEY_TAG, value)
    }

    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }))
    }
  }

  const validateForm = () => {
    const nextErrors = {}

    if (!formData.tag) {
      nextErrors.tag = 'Select or create a configuration tag before recording.'
    }

    if (!Number.isFinite(formData.duration) || formData.duration <= 0) {
      nextErrors.duration = 'Duration must be a positive number of seconds.'
    } else if (formData.duration > 3600) {
      nextErrors.duration = 'Duration is capped at 3600 seconds (1 hour).'
    }

    if (
      !Number.isInteger(formData.maxRestarts) ||
      formData.maxRestarts < 1 ||
      formData.maxRestarts > 20
    ) {
      nextErrors.maxRestarts = 'Max restarts must be an integer between 1 and 20.'
    }

    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const resetForm = () => {
    setFormData({ ...INITIAL_FORM })
    setErrors({})
    setStatus(STATUS.IDLE)
    setStatusMessage('')
    setResultImage(null)
    setResultMeta(null)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!validateForm()) return

    setStatus(STATUS.RECORDING)
    setStatusMessage('Starting spectrogram recording...')
    setResultImage(null)
    setResultMeta(null)

    const payload = {
      tags: [formData.tag],
      duration: formData.duration,
      force_restart: formData.forceRestart,
      max_restarts: formData.maxRestarts,
      validate: formData.validate
    }

    try {
      await apiClient.recordSpectrogram(payload)

      setStatus(STATUS.PLOTTING)
      setStatusMessage('Recording complete. Generating PNG snapshot...')

      const window = getObservationWindow(formData.duration)
      const plotPayload = {
        tags: [formData.tag],
        obs_date: window.obs_date,
        start_time: window.start_time,
        end_time: window.end_time
      }

      const response = await apiClient.createPlot(plotPayload)
      setResultImage(response.data)
      setResultMeta({
        tag: formData.tag,
        duration: formData.duration,
        start: window.start_iso,
        end: window.end_iso
      })

      setStatus(STATUS.COMPLETE)
      setStatusMessage('Spectrogram ready.')
      if (onRecordingComplete) {
        onRecordingComplete()
      }
    } catch (error) {
      setStatus(STATUS.ERROR)
      setStatusMessage(error.message || 'Something went wrong. Please try again.')
    }
  }

  const isBusy =
    status === STATUS.RECORDING || status === STATUS.PLOTTING

  return (
    <div className="recording-form">
      <form onSubmit={handleSubmit} noValidate>
        <div className="form-group">
          <label htmlFor="tag">Configuration Tag</label>
          <select
            id="tag"
            name="tag"
            value={formData.tag}
            onChange={handleChange}
            disabled={isBusy}
            className={errors.tag ? 'error' : ''}
          >
            <option value="">Select a configuration...</option>
            {availableTags.map((tag) => (
              <option key={tag} value={tag}>
                {tag}
              </option>
            ))}
          </select>
          {errors.tag && <span className="error-message">{errors.tag}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="duration">Duration (seconds)</label>
          <input
            type="number"
            id="duration"
            name="duration"
            min="1"
            max="3600"
            step="1"
            value={formData.duration}
            onChange={handleChange}
            disabled={isBusy}
            className={errors.duration ? 'error' : ''}
          />
          {errors.duration && (
            <span className="error-message">{errors.duration}</span>
          )}
        </div>

        <details className="form-details">
          <summary>Advanced options</summary>
          <div className="form-group checkbox">
            <label htmlFor="forceRestart">
              <input
                type="checkbox"
                id="forceRestart"
                name="forceRestart"
                checked={formData.forceRestart}
                onChange={handleChange}
                disabled={isBusy}
              />
              Force restart on worker failure
            </label>
          </div>

          <div className="form-group">
            <label htmlFor="maxRestarts">Max restarts</label>
            <input
              type="number"
              id="maxRestarts"
              name="maxRestarts"
              min="1"
              max="20"
              step="1"
              value={formData.maxRestarts}
              onChange={handleChange}
              disabled={isBusy}
              className={errors.maxRestarts ? 'error' : ''}
            />
            {errors.maxRestarts && (
              <span className="error-message">{errors.maxRestarts}</span>
            )}
          </div>

          <div className="form-group checkbox">
            <label htmlFor="validate">
              <input
                type="checkbox"
                id="validate"
                name="validate"
                checked={formData.validate}
                onChange={handleChange}
                disabled={isBusy}
              />
              Validate configuration before recording
            </label>
          </div>
        </details>

        <div className="form-actions">
          <button type="submit" className="start-button" disabled={isBusy}>
            {isBusy ? 'Working...' : 'Start'}
          </button>
          <button
            type="button"
            className="reset-button"
            onClick={resetForm}
            disabled={isBusy && status !== STATUS.ERROR}
          >
            Reset
          </button>
        </div>
      </form>

      {statusMessage && (
        <div className={`status-message ${status}`}>
          {statusMessage}
        </div>
      )}

      {resultImage && (
        <div className="result-section">
          <h3>Latest PNG</h3>
          <img src={resultImage} alt="Spectrogram result" loading="lazy" />
          {resultMeta && (
            <p className="result-info">
              Tag {resultMeta.tag} · {resultMeta.duration}s ·{' '}
              {new Date(resultMeta.start).toUTCString()} ➜{' '}
              {new Date(resultMeta.end).toUTCString()}
            </p>
          )}
        </div>
      )}
    </div>
  )
}

export default RecordingForm
