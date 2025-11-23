import React, { useState, useEffect } from 'react'
import { apiClient } from '../services/apiClient'

function LogViewer() {
  const [logFiles, setLogFiles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedLog, setSelectedLog] = useState(null)
  const [logContent, setLogContent] = useState(null)
  const [loadingContent, setLoadingContent] = useState(false)
  const [processTypeFilter, setProcessTypeFilter] = useState('')
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [allLogs, setAllLogs] = useState([]) // Store all logs for client-side pagination
  const logsPerPage = 5

  useEffect(() => {
    setCurrentPage(1) // Reset to page 1 when filter changes
    loadLogs()
  }, [processTypeFilter])

  // Load list of log files
  const loadLogs = async () => {
    try {
      setLoading(true)
      setError(null)

      const processType = processTypeFilter || null
      const response = await apiClient.getLogs(processType)
      const logs = response.data || []

      // Store all logs for pagination
      setAllLogs(logs)

      // Set paginated logs for current page
      updatePaginatedLogs(logs, 1) // Start at page 1
    } catch (err) {
      setError(`Failed to load logs: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  // Update displayed logs based on current page
  const updatePaginatedLogs = (logs, page) => {
    const startIndex = (page - 1) * logsPerPage
    const endIndex = startIndex + logsPerPage
    const paginatedLogs = logs.slice(startIndex, endIndex)
    setLogFiles(paginatedLogs)
    setCurrentPage(page)
  }

  // Calculate pagination metadata
  const getPaginationMetadata = () => {
    const totalLogs = allLogs.length
    const totalPages = Math.ceil(totalLogs / logsPerPage)
    const hasPrev = currentPage > 1
    const hasNext = currentPage < totalPages

    return { totalLogs, totalPages, hasPrev, hasNext }
  }

  // Load content of a specific log file
  const handleLogClick = async (fileName) => {
    try {
      setLoadingContent(true)
      setSelectedLog(fileName)

      const response = await apiClient.getLogContent(fileName)
      setLogContent(response.data || '')
    } catch (err) {
      setError(`Failed to load log content: ${err.message}`)
      setLogContent(null)
    } finally {
      setLoadingContent(false)
    }
  }

  // Close log content view
  const handleCloseLog = () => {
    setSelectedLog(null)
    setLogContent(null)
  }

  // Download log file
  const handleDownload = (fileName) => {
    const blob = new Blob([logContent], { type: 'text/plain' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  // Pagination handlers
  const handleNextPage = () => {
    const { hasNext } = getPaginationMetadata()
    if (hasNext) {
      const nextPage = currentPage + 1
      updatePaginatedLogs(allLogs, nextPage)
    }
  }

  const handlePrevPage = () => {
    const { hasPrev } = getPaginationMetadata()
    if (hasPrev) {
      const prevPage = currentPage - 1
      updatePaginatedLogs(allLogs, prevPage)
    }
  }

  if (loading) {
    return (
      <section className="logs-section">
        <h2>System Logs</h2>
        <div className="loading">Loading logs...</div>
      </section>
    )
  }

  return (
    <section className="logs-section">
      <div className="logs-header">
        <h2>System Logs</h2>
        <div className="logs-controls">
          <select
            value={processTypeFilter}
            onChange={(e) => setProcessTypeFilter(e.target.value)}
            className="log-filter-select"
            title="Filter by log type"
          >
            <option value="">All Logs</option>
            <option value="worker">Worker Logs</option>
            <option value="user">User Logs</option>
          </select>
          <button
            onClick={loadLogs}
            className="refresh-button"
            title="Refresh log list"
          >
            ↻ Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="error">
          <p>{error}</p>
          <button onClick={loadLogs}>Retry</button>
        </div>
      )}

      {logFiles.length === 0 ? (
        <p className="no-logs">No log files found.</p>
      ) : (
        <>
          <div className="logs-list">
            {logFiles.map((logFile) => (
              <div key={logFile} className="log-item">
                <span className="log-name">{logFile}</span>
                <button
                  className="view-log-button"
                  onClick={() => handleLogClick(logFile)}
                  title="View log content"
                >
                  👁 View
                </button>
              </div>
            ))}
          </div>

          {getPaginationMetadata().totalPages > 1 && (
            <div className="pagination-controls">
              <button
                className="pagination-button"
                onClick={handlePrevPage}
                disabled={!getPaginationMetadata().hasPrev}
                title="Previous page"
              >
                ← Previous
              </button>

              <span className="pagination-info">
                Page {currentPage} of {getPaginationMetadata().totalPages}
                <span className="pagination-total"> ({getPaginationMetadata().totalLogs} total)</span>
              </span>

              <button
                className="pagination-button"
                onClick={handleNextPage}
                disabled={!getPaginationMetadata().hasNext}
                title="Next page"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}

      {selectedLog && (
        <div
          className="log-modal-overlay"
          onClick={handleCloseLog}
        >
          <div className="log-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="log-modal-header">
              <h3>{selectedLog}</h3>
              <button className="modal-close" onClick={handleCloseLog}>
                ×
              </button>
            </div>

            <div className="log-modal-body">
              {loadingContent ? (
                <div className="loading">Loading log content...</div>
              ) : (
                <pre className="log-content">{logContent}</pre>
              )}
            </div>

            <div className="log-modal-footer">
              <button
                className="modal-button modal-button-download"
                onClick={() => handleDownload(selectedLog)}
                disabled={!logContent}
              >
                ⬇ Download
              </button>
              <button
                className="modal-button modal-button-cancel"
                onClick={handleCloseLog}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}

export default LogViewer
