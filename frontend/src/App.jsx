import React, { useState, useEffect } from 'react'
import RecordingForm from './components/RecordingForm'
import ConfigManager from './components/ConfigManager'
import SavedSpectrograms from './components/SavedSpectrograms'
import LogViewer from './components/LogViewer'
import FriendlyError from './components/FriendlyError'
import { apiClient } from './services/apiClient'

function App() {
  const [configs, setConfigs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const [darkMode, setDarkMode] = useState(() => {
    // Initialize from localStorage or default to false
    const saved = localStorage.getItem('darkMode')
    return saved ? JSON.parse(saved) : false
  })

  useEffect(() => {
    loadInitialData()
  }, [])

  // Apply dark mode class to body
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode')
    } else {
      document.body.classList.remove('dark-mode')
    }
    // Save preference to localStorage
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
  }, [darkMode])

  const loadInitialData = async () => {
    try {
      setLoading(true)

      // Load available configurations
      const configsResponse = await apiClient.getConfigs()
      setConfigs(configsResponse.data || [])

    } catch (err) {
      setError(err.message || 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  const handleRecordingComplete = () => {
    // Trigger refresh of SavedSpectrograms component
    setRefreshKey(prev => prev + 1)
  }

  const handleConfigsChange = async () => {
    // Reload configs when they change in ConfigManager
    try {
      const configsResponse = await apiClient.getConfigs()
      setConfigs(configsResponse.data || [])
    } catch (err) {
      console.error('Failed to reload configs:', err)
    }
  }

  const toggleDarkMode = () => {
    setDarkMode(prev => !prev)
  }

  if (loading) {
    return (
      <div className="app">
        <header className="header">
          <h1>Spectre - Radio Spectrogram Recording</h1>
          <button className="dark-mode-toggle" onClick={toggleDarkMode}>
            {darkMode ? '☀️ Light' : '🌙 Dark'}
          </button>
        </header>
        <main className="main">
          <div className="loading">Loading...</div>
        </main>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app">
        <header className="header">
          <h1>Spectre - Radio Spectrogram Recording</h1>
          <button className="dark-mode-toggle" onClick={toggleDarkMode}>
            {darkMode ? '☀️ Light' : '🌙 Dark'}
          </button>
        </header>
        <main className="main">
          <FriendlyError
            title="Spectre couldn't load its starting configs."
            detail={error}
            onRetry={() => {
              setError(null)
              loadInitialData()
            }}
          />
        </main>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Spectre - Radio Spectrogram Recording</h1>
        <p>Process, Explore and Capture Transient Radio Emissions</p>
        <button className="dark-mode-toggle" onClick={toggleDarkMode}>
          {darkMode ? '☀️ Light' : '🌙 Dark'}
        </button>
      </header>

      <main className="main">
        <section className="recording-config-section">
          <h2>Recording & Configuration</h2>
          <div className="recording-config-grid">
            <div className="recording-panel">
              <h3>Start New Recording</h3>
              <RecordingForm
                configs={configs}
                onRecordingComplete={handleRecordingComplete}
              />
            </div>
            <div className="config-panel">
              <ConfigManager onConfigsChange={handleConfigsChange} />
            </div>
          </div>
        </section>

        <SavedSpectrograms key={refreshKey} />

        <LogViewer />
      </main>

      <footer className="footer">
        <p>
          Built by <a href="https://github.com/b3p3k0/spectre" target="_blank" rel="noreferrer">Spectre WebUI</a>
          {' '}with gratitude to the
          {' '}<a href="https://github.com/jcfitzpatrick12/spectre" target="_blank" rel="noreferrer">original Spectre project</a>
          {' '}and the
          {' '}<a href="https://www.reddit.com/r/vibecoding/" target="_blank" rel="noreferrer">r/vibecoding</a> community.
        </p>
      </footer>
    </div>
  )
}

export default App
