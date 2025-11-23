import React, { useState, useEffect } from 'react'
import { apiClient } from '../services/apiClient'
import FriendlyError from './FriendlyError'

function SavedSpectrograms() {
  const [recordings, setRecordings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lightboxUrl, setLightboxUrl] = useState(null)
  const [refreshing, setRefreshing] = useState(false)
  const [sortOrder, setSortOrder] = useState('newest')
  // Delete confirmation dialog state: {url, filename} or null
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  const [deleting, setDeleting] = useState(false)
  // Filter state
  const [filters, setFilters] = useState({
    year: '',
    month: '',
    day: '',
    tags: []
  })
  const [availableTags, setAvailableTags] = useState([])
  const [showFilters, setShowFilters] = useState(false)
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [pagination, setPagination] = useState(null)

  useEffect(() => {
    loadRecordings()
    loadAvailableTags()
  }, [])

  // Load available tags for filter dropdown
  const loadAvailableTags = async () => {
    try {
      const response = await apiClient.getTags()
      setAvailableTags(response.data || [])
    } catch (err) {
      // Non-critical - filter will still work with manual tag entry
      console.warn('Failed to load tags:', err.message)
    }
  }

  const loadRecordings = async (filterParams = null, page = 1) => {
    try {
      setLoading(true)
      setError(null)

      // Use provided filters or current state filters
      const activeFilters = filterParams !== null ? filterParams : filters

      // Build API parameters
      const extensions = ['png']
      const tags = activeFilters.tags || []
      const year = activeFilters.year || null
      const month = activeFilters.month || null
      const day = activeFilters.day || null

      const response = await apiClient.getBatchFiles(extensions, tags, year, month, day, page, 9)

      // Handle paginated response structure
      if (response.data && response.data.items && response.data.pagination) {
        setRecordings(response.data.items)
        setPagination(response.data.pagination)
        setCurrentPage(response.data.pagination.current_page)
      } else {
        // Fallback for non-paginated response (backward compatibility)
        setRecordings(response.data || [])
        setPagination(null)
      }
    } catch (err) {
      setError(err.message || 'Failed to load recordings')
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    try {
      setRefreshing(true)
      await loadRecordings(null, currentPage)
    } catch (err) {
      setError(err.message || 'Failed to refresh recordings')
    } finally {
      setRefreshing(false)
    }
  }

  // Apply filters and reload recordings (reset to page 1)
  const handleApplyFilters = () => {
    setCurrentPage(1)
    loadRecordings(filters, 1)
  }

  // Clear all filters and reload (reset to page 1)
  const handleClearFilters = () => {
    const emptyFilters = {
      year: '',
      month: '',
      day: '',
      tags: []
    }
    setFilters(emptyFilters)
    setCurrentPage(1)
    loadRecordings(emptyFilters, 1)
  }

  // Check if any filters are active
  const hasActiveFilters = () => {
    return filters.year || filters.month || filters.day || filters.tags.length > 0
  }

  // Handle tag selection change
  const handleTagChange = (e) => {
    const selectedOptions = Array.from(e.target.selectedOptions, option => option.value)
    setFilters(prev => ({ ...prev, tags: selectedOptions }))
  }

  // Pagination handlers
  const handleNextPage = () => {
    if (pagination?.has_next) {
      const nextPage = currentPage + 1
      setCurrentPage(nextPage)
      loadRecordings(null, nextPage)
    }
  }

  const handlePrevPage = () => {
    if (pagination?.has_prev) {
      const prevPage = currentPage - 1
      setCurrentPage(prevPage)
      loadRecordings(null, prevPage)
    }
  }

  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'newest' ? 'oldest' : 'newest')
    // Note: Sorting is client-side so no need to reload or change page
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

  // Handle delete button click - show confirmation dialog
  const handleDeleteClick = (url) => {
    const filename = url.split('/').pop()
    setDeleteConfirm({ url, filename })
  }

  // Perform the actual deletion after confirmation
  const handleDeleteConfirm = async () => {
    if (!deleteConfirm) return

    try {
      setDeleting(true)
      setError(null)

      // Call API to delete the file (pessimistic update - wait for success)
      await apiClient.deleteBatchFile(deleteConfirm.filename)

      // Close lightbox if deleted file was open
      if (lightboxUrl === deleteConfirm.url) {
        setLightboxUrl(null)
      }

      // Close confirmation dialog
      setDeleteConfirm(null)

      // Reload current page to reflect the deletion
      await loadRecordings(null, currentPage)
    } catch (err) {
      setError(err.message || 'Failed to delete recording')
      // Keep dialog open so user can retry or cancel
    } finally {
      setDeleting(false)
    }
  }

  // Cancel deletion
  const handleDeleteCancel = () => {
    setDeleteConfirm(null)
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
        <FriendlyError
          title="The gallery needs a second."
          detail={error}
          onRetry={() => {
            setError(null)
            loadRecordings(filters, currentPage)
          }}
          onDismiss={() => setError(null)}
        />
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
              className="filter-toggle-button"
              onClick={() => setShowFilters(!showFilters)}
              title="Toggle filters"
            >
              {showFilters ? '🔽 Hide Filters' : '🔼 Show Filters'}
              {hasActiveFilters() && <span className="filter-badge">●</span>}
            </button>
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

        {showFilters && (
          <div className="filters-section">
            <div className="filters-grid">
              <div className="filter-group">
                <label htmlFor="filter-year">Year</label>
                <input
                  id="filter-year"
                  type="number"
                  placeholder="YYYY (e.g., 2025)"
                  value={filters.year}
                  onChange={(e) => setFilters(prev => ({ ...prev, year: e.target.value }))}
                  min="2020"
                  max="2099"
                />
              </div>

              <div className="filter-group">
                <label htmlFor="filter-month">Month</label>
                <input
                  id="filter-month"
                  type="number"
                  placeholder="MM (1-12)"
                  value={filters.month}
                  onChange={(e) => setFilters(prev => ({ ...prev, month: e.target.value }))}
                  min="1"
                  max="12"
                />
              </div>

              <div className="filter-group">
                <label htmlFor="filter-day">Day</label>
                <input
                  id="filter-day"
                  type="number"
                  placeholder="DD (1-31)"
                  value={filters.day}
                  onChange={(e) => setFilters(prev => ({ ...prev, day: e.target.value }))}
                  min="1"
                  max="31"
                />
              </div>

              <div className="filter-group filter-group-tags">
                <label htmlFor="filter-tags">Tags</label>
                <select
                  id="filter-tags"
                  multiple
                  value={filters.tags}
                  onChange={handleTagChange}
                  size="3"
                >
                  {availableTags.length === 0 ? (
                    <option disabled>No tags available</option>
                  ) : (
                    availableTags.map(tag => (
                      <option key={tag} value={tag}>{tag}</option>
                    ))
                  )}
                </select>
                <small className="filter-hint">Hold Ctrl/Cmd to select multiple</small>
              </div>
            </div>

            <div className="filters-actions">
              <button
                className="apply-filters-button"
                onClick={handleApplyFilters}
              >
                Apply Filters
              </button>
              <button
                className="clear-filters-button"
                onClick={handleClearFilters}
                disabled={!hasActiveFilters()}
              >
                Clear Filters
              </button>
            </div>

            {hasActiveFilters() && (
              <div className="active-filters">
                <strong>Active Filters:</strong>
                {filters.year && <span className="filter-pill">Year: {filters.year}</span>}
                {filters.month && <span className="filter-pill">Month: {filters.month}</span>}
                {filters.day && <span className="filter-pill">Day: {filters.day}</span>}
                {filters.tags.map(tag => (
                  <span key={tag} className="filter-pill">Tag: {tag}</span>
                ))}
              </div>
            )}
          </div>
        )}

        {recordings.length === 0 ? (
          <p className="no-recordings">No recordings yet. Start your first recording above!</p>
        ) : (
          <>
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

                      <div className="recording-actions">
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
                        <button
                          className="delete-button"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteClick(recording);
                          }}
                          title="Delete recording"
                        >
                          🗑 Delete
                        </button>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>

            {pagination && pagination.total_pages > 1 && (
              <div className="pagination-controls">
                <button
                  className="pagination-button"
                  onClick={handlePrevPage}
                  disabled={!pagination.has_prev}
                  title="Previous page"
                >
                  ← Previous
                </button>

                <span className="pagination-info">
                  Page {pagination.current_page} of {pagination.total_pages}
                  <span className="pagination-total"> ({pagination.total_items} total)</span>
                </span>

                <button
                  className="pagination-button"
                  onClick={handleNextPage}
                  disabled={!pagination.has_next}
                  title="Next page"
                >
                  Next →
                </button>
              </div>
            )}
          </>
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

      {deleteConfirm && (
        <div
          className="modal-overlay"
          role="dialog"
          aria-label="Delete confirmation"
          onClick={handleDeleteCancel}
        >
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Delete Recording?</h3>
            <p>Are you sure you want to delete this recording?</p>
            <p className="modal-filename"><strong>{deleteConfirm.filename}</strong></p>
            <p className="modal-warning">This action cannot be undone.</p>

            <div className="modal-actions">
              <button
                className="modal-button modal-button-cancel"
                onClick={handleDeleteCancel}
                disabled={deleting}
              >
                Cancel
              </button>
              <button
                className="modal-button modal-button-delete"
                onClick={handleDeleteConfirm}
                disabled={deleting}
              >
                {deleting ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default SavedSpectrograms
