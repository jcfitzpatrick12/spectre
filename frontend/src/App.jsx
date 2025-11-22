import React, { useState, useEffect } from 'react'
import RecordingForm from './components/RecordingForm'
import SavedSpectrograms from './components/SavedSpectrograms'
import { apiClient } from './services/apiClient'

function App() {
  const [configs, setConfigs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    try {
      setLoading(true)

      // Load available configurations
      const configsResponse = await apiClient.getConfigs()
      setConfigs(configsResponse.data || [])

    } catch (err) {
      setError(`Failed to load initial data: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleRecordingComplete = () => {
    // Trigger refresh of SavedSpectrograms component
    setRefreshKey(prev => prev + 1)
  }

  if (loading) {
    return (
      <div className="app">
        <header className="header">
          <h1>Spectre - Radio Spectrogram Recording</h1>
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
        </header>
        <main className="main">
          <div className="error">
            <p>{error}</p>
            <button onClick={() => {setError(null); loadInitialData()}}>
              Retry
            </button>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Spectre - Radio Spectrogram Recording</h1>
        <p>Process, Explore and Capture Transient Radio Emissions</p>
      </header>

      <main className="main">
        <section className="recording-section">
          <h2>Start New Recording</h2>
          <RecordingForm
            configs={configs}
            onRecordingComplete={handleRecordingComplete}
          />
        </section>

        <SavedSpectrograms key={refreshKey} />
      </main>
    </div>
  )
}

export default App
