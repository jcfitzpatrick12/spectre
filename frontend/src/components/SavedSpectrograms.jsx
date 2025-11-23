import React, { useState, useEffect } from 'react'
import { apiClient } from '../services/apiClient'

function SavedSpectrograms() {
  const [recordings, setRecordings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lightboxUrl, setLightboxUrl] = useState(null)
  const [refreshing, setRefreshing] = useState(false)
  const [sortOrder, setSortOrder] = useState('newest')

  useEffect(() => {
    loadRecordings()
  }, [])

  const loadRecordings = async () => {
    try {
      setLoading(true)
      setError(null)

      const batchFiles = await apiClient.getBatchFiles(['png'])
      setRecordings(batchFiles.data || [])
    } catch (err) {
      setError(`Failed to load recordings: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    try {
      setRefreshing(true)
      setError(null)

      const batchFiles = await apiClient.getBatchFiles(['png'])
      setRecordings(batchFiles.data || [])
    } catch (err) {
      setError(`Failed to refresh recordings: ${err.message}`)
    } finally {
      setRefreshing(false)
    }
  }

  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'newest' ? 'oldest' : 'newest')
  }

  const getSortedRecordings = () => {
    const sorted = [...recordings].sort((a, b) => {
      // URLs contain filenames with format: YYYYMMDD_HHMMSS_tag.png
      // These are already sortable strings
      return sortOrder === 'newest'
        ? b.localeCompare(a)  // Descending (newest first)
        : a.localeCompare(b)  // Ascending (oldest first)
    })
    return sorted
  }

  const parseMetadata = (url) => {
    // Extract filename from URL
    const filename = url.split('/').pop()

    // Filename format: YYYYMMDD_HHMMSS_tag.png
    // Example: 20250122_143052_callisto.png
    const match = filename.match(/^(\d{8})_(\d{6})_(.+)\.png$/)

    if (match) {
      const [, datePart, timePart, tag] = match

      // Parse date: YYYYMMDD
      const year = datePart.substring(0, 4)
      const month = datePart.substring(4, 6)
      const day = datePart.substring(6, 8)

      // Parse time: HHMMSS
      const hours = timePart.substring(0, 2)
      const minutes = timePart.substring(2, 4)
      const seconds = timePart.substring(4, 6)

      return {
        filename,
        tag,
        timestamp: `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`,
        date: `${year}-${month}-${day}`,
        time: `${hours}:${minutes}:${seconds}`
      }
    }

    // Fallback for non-standard filenames
    return {
      filename,
      tag: 'Unknown',
      timestamp: 'Unknown',
      date: 'Unknown',
      time: 'Unknown'
    }
  }

  const handleDownload = async (url) => {
    try {
      const filename = url.split('/').pop()

      // Fetch the image as a blob
      const response = await fetch(url)
      if (!response.ok) throw new Error('Download failed')

      const blob = await response.blob()

      // Create download link
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      // Clean up
      window.URL.revokeObjectURL(downloadUrl)
    } catch (err) {
      alert(`Download failed: ${err.message}`)
    }
  }

  if (loading) {
    return (
      <section className="gallery-section">
        <h2>Previous Recordings</h2>
        <div className="loading">Loading recordings...</div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="gallery-section">
        <h2>Previous Recordings</h2>
        <div className="error">
          <p>{error}</p>
          <button onClick={loadRecordings}>Retry</button>
        </div>
      </section>
    )
  }

  return (
    <>
      <section className="gallery-section">
        <div className="gallery-header">
          <h2>Previous Recordings</h2>
          <div className="gallery-controls">
            <button
              className="sort-button"
              onClick={toggleSortOrder}
              title={`Sort by ${sortOrder === 'newest' ? 'oldest' : 'newest'} first`}
            >
              {sortOrder === 'newest' ? '↓ Newest First' : '↑ Oldest First'}
            </button>
            <button
              className="refresh-button"
              onClick={handleRefresh}
              disabled={refreshing}
              title="Refresh recordings list"
            >
              {refreshing ? '↻ Refreshing...' : '↻ Refresh'}
            </button>
          </div>
        </div>

        {recordings.length === 0 ? (
          <p className="no-recordings">No recordings yet. Start your first recording above!</p>
        ) : (
          <div className="recordings-grid">
            {getSortedRecordings().map((recording, index) => {
              const metadata = parseMetadata(recording)

              return (
                <div key={index} className="recording-card">
                  <button
                    type="button"
                    className="recording-preview"
                    onClick={() => setLightboxUrl(recording)}
                    title="Click to view full size"
                  >
                    <img
                      src={recording}
                      alt={`Recording ${metadata.tag} - ${metadata.timestamp}`}
                      loading="lazy"
                    />
                  </button>

                  <div className="recording-info">
                    <p className="recording-tag">
                      <strong>{metadata.tag}</strong>
                    </p>
                    <p className="recording-timestamp">
                      {metadata.timestamp}
                    </p>
                    <p className="recording-filename">{metadata.filename}</p>

                    <button
                      className="download-button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDownload(recording);
                      }}
                      title="Download PNG file"
                    >
                      ⬇ Download
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </section>

      {lightboxUrl && (
        <div
          className="lightbox"
          role="dialog"
          aria-label="Spectrogram preview"
          onClick={() => setLightboxUrl(null)}
        >
          <div className="lightbox-content" onClick={(e) => e.stopPropagation()}>
            <button className="lightbox-close" onClick={() => setLightboxUrl(null)}>
              ×
            </button>
            <img
              src={lightboxUrl}
              alt="Spectrogram full view"
            />
            <div className="lightbox-info">
              <p className="filename">{parseMetadata(lightboxUrl).filename}</p>
              <button
                className="lightbox-download"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDownload(lightboxUrl);
                }}
              >
                ⬇ Download
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default SavedSpectrograms
