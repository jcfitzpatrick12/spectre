import React, { useEffect, useMemo, useState, useRef } from 'react'
import { apiClient } from '../services/apiClient'

const STATUS = {
  IDLE: 'idle',
  RECORDING: 'recording',
  PLOTTING: 'plotting',
  COMPLETE: 'complete',
  ERROR: 'error'
}

const STORAGE_KEY_TAG = 'spectre.selectedTag'
const STORAGE_KEY_JOB = 'spectre.activeJobId'
const POLL_INTERVAL_MS = 5000  // Poll every 5 seconds

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
  const [currentJobId, setCurrentJobId] = useState(null)
  const [progress, setProgress] = useState(0)
  const [recordingStartTime, setRecordingStartTime] = useState(null)
  const pollingIntervalRef = useRef(null)

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

  // Recover in-progress job on mount
  useEffect(() => {
    const savedJob = localStorage.getItem(STORAGE_KEY_JOB)
    if (!savedJob) return

    try {
      const { jobId, tag, duration, startTime } = JSON.parse(savedJob)

      // Restore job state
      setCurrentJobId(jobId)
      setStatus(STATUS.RECORDING)
      setRecordingStartTime(new Date(startTime))
      setStatusMessage('Reconnecting to in-progress recording...')

      // Check if job still exists
      pollJobStatus(jobId).catch((error) => {
        console.error('Failed to recover job:', error)
        setStatus(STATUS.ERROR)
        setStatusMessage('Failed to reconnect to recording. It may have completed or failed.')
        localStorage.removeItem(STORAGE_KEY_JOB)
      })

      // Start polling
      pollingIntervalRef.current = setInterval(() => {
        pollJobStatus(jobId)
      }, POLL_INTERVAL_MS)
    } catch (error) {
      console.error('Failed to parse saved job:', error)
      localStorage.removeItem(STORAGE_KEY_JOB)
    }
  }, [])

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
      }
    }
  }, [])

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

  const validateForm = async () => {
    const nextErrors = {}

    if (!formData.tag) {
      nextErrors.tag = 'Select or create a configuration tag before recording.'
    }

    if (!Number.isFinite(formData.duration) || formData.duration <= 0) {
      nextErrors.duration = 'Duration must be a positive number of seconds.'
    } else if (formData.duration > 28800) {
      nextErrors.duration = 'Duration is capped at 28800 seconds (8 hours).'
    } else if (formData.tag) {
      // Validate duration against batch_size constraints
      try {
        const configResponse = await apiClient.getConfigRaw(formData.tag)
        const config = configResponse.data  // Already parsed by apiClient
        const batchSize = config.parameters?.batch_size

        if (batchSize && formData.duration % batchSize !== 0) {
          nextErrors.duration = `Duration must be a multiple of ${batchSize} seconds (your config's batch size). Try: ${batchSize * 2}s, ${batchSize * 4}s, ${batchSize * 10}s, etc.`
        } else if (batchSize && formData.duration < batchSize * 2) {
          nextErrors.duration = `Duration should be at least ${batchSize * 2} seconds (2× batch size) for reliable results. Try: ${batchSize * 2}s, ${batchSize * 4}s, ${batchSize * 10}s.`
        }
      } catch (err) {
        // If we can't fetch config, skip batch_size validation
        console.warn('Could not validate batch_size:', err.message)
      }
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
    setCurrentJobId(null)
    setProgress(0)
    setRecordingStartTime(null)
    localStorage.removeItem(STORAGE_KEY_JOB)
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
      pollingIntervalRef.current = null
    }
  }

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`
    }
    if (minutes > 0) {
      return `${minutes}m ${secs}s`
    }
    return `${secs}s`
  }

  const pollJobStatus = async (jobId) => {
    try {
      const response = await apiClient.getJobStatus(jobId)
      const job = response.data

      setProgress(job.progress || 0)

      if (job.status === 'running') {
        const elapsed = job.progress ? (job.duration * job.progress / 100) : 0
        const remaining = job.duration - elapsed
        setStatusMessage(
          `Recording: ${Math.round(job.progress)}% complete (${formatDuration(elapsed)} / ${formatDuration(job.duration)}) - ${formatDuration(remaining)} remaining`
        )
      } else if (job.status === 'completed') {
        // Recording completed, now create plot
        setStatus(STATUS.PLOTTING)
        setStatusMessage('Recording complete. Generating PNG snapshot...')
        setProgress(100)

        // Stop polling
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current)
          pollingIntervalRef.current = null
        }

        // Generate plot
        await createPlot(recordingStartTime, formData.duration, formData.tag)

        setStatus(STATUS.COMPLETE)
        setStatusMessage('Spectrogram ready.')
        setCurrentJobId(null)
        localStorage.removeItem(STORAGE_KEY_JOB)

        if (onRecordingComplete) {
          onRecordingComplete()
        }
      } else if (job.status === 'failed' || job.status === 'cancelled') {
        // Recording failed or was cancelled
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current)
          pollingIntervalRef.current = null
        }

        setStatus(STATUS.ERROR)
        setStatusMessage(
          job.error || `Recording ${job.status}. Please try again.`
        )
        setCurrentJobId(null)
        localStorage.removeItem(STORAGE_KEY_JOB)
      }
    } catch (error) {
      console.error('Error polling job status:', error)
      // Don't stop polling on transient errors, just log them
    }
  }

  const createPlot = async (startTime, duration, tag) => {
    const recordingEndTime = new Date(startTime.getTime() + duration * 1000)
    const [startDate, startTimeRaw] = startTime.toISOString().split('T')
    const [, endTimeRaw] = recordingEndTime.toISOString().split('T')

    const plotPayload = {
      tags: [tag],
      obs_date: startDate,
      start_time: startTimeRaw.split('.')[0],
      end_time: endTimeRaw.split('.')[0]
    }

    await apiClient.createPlot(plotPayload)
  }

  const cancelRecording = async () => {
    if (!currentJobId) return

    try {
      await apiClient.cancelJob(currentJobId)

      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
        pollingIntervalRef.current = null
      }

      setStatus(STATUS.IDLE)
      setStatusMessage('Recording cancelled.')
      setCurrentJobId(null)
      setProgress(0)
      localStorage.removeItem(STORAGE_KEY_JOB)
    } catch (error) {
      setStatusMessage('Failed to cancel recording: ' + error.message)
    }
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!(await validateForm())) return

    setStatus(STATUS.RECORDING)
    setStatusMessage('Starting async spectrogram recording...')
    setProgress(0)

    const payload = {
      tags: [formData.tag],
      duration: formData.duration,
      force_restart: formData.forceRestart,
      max_restarts: formData.maxRestarts,
      validate: formData.validate
    }

    try {
      // Capture the exact moment recording starts
      const startTime = new Date()
      setRecordingStartTime(startTime)

      // Start async recording (returns immediately with job_id)
      const response = await apiClient.recordSpectrogramAsync(payload)
      const job = response.data

      // Save job ID
      setCurrentJobId(job.job_id)
      localStorage.setItem(STORAGE_KEY_JOB, JSON.stringify({
        jobId: job.job_id,
        tag: formData.tag,
        duration: formData.duration,
        startTime: startTime.toISOString()
      }))

      // Start polling for job status
      setStatusMessage('Recording started. Monitoring progress...')
      pollingIntervalRef.current = setInterval(() => {
        pollJobStatus(job.job_id)
      }, POLL_INTERVAL_MS)

      // Poll immediately for first update
      pollJobStatus(job.job_id)
    } catch (error) {
      setStatus(STATUS.ERROR)
      setStatusMessage(error.message || 'Failed to start recording. Please try again.')
    }
  }

  const isBusy =
    status === STATUS.RECORDING || status === STATUS.PLOTTING

  return (
    <div className="recording-form">
      <form onSubmit={handleSubmit} noValidate>
        <div className="form-group">
          <label htmlFor="tag">
            Configuration Tag
            <span
              className="helper-tooltip"
              title="Tags bundle receiver hardware, center frequency, and gain settings. Pick one you saved in the CLI."
            >?</span>
          </label>
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
          <label htmlFor="duration">
            Duration (seconds)
            <span
              className="helper-tooltip"
              title="How long Spectre listens before drawing your PNG snapshot."
            >?</span>
          </label>
          <input
            type="number"
            id="duration"
            name="duration"
            min="1"
            max="28800"
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
              <span
                className="helper-tooltip"
                title="If a worker hangs, this tells Spectre to stop and launch a fresh one instead of waiting."
              >?</span>
            </label>
          </div>

          <div className="form-group">
            <label htmlFor="maxRestarts">
              Max restarts
              <span
                className="helper-tooltip"
                title="Safety valve for how many times Spectre retries a flaky receiver before giving up."
              >?</span>
            </label>
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
              <span
                className="helper-tooltip"
                title="Spectre double-checks the config against your hardware before starting."
              >?</span>
            </label>
          </div>
        </details>

        <div className="form-actions">
          <button type="submit" className="start-button" disabled={isBusy}>
            {isBusy ? 'Working...' : 'Start'}
          </button>
          {status === STATUS.RECORDING && currentJobId && (
            <button
              type="button"
              className="cancel-button"
              onClick={cancelRecording}
            >
              Cancel
            </button>
          )}
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
          {status === STATUS.RECORDING && progress > 0 && (
            <div className="progress-bar-container">
              <div
                className="progress-bar"
                style={{ width: `${progress}%` }}
              />
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default RecordingForm
