class ApiClient {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl
  }

  async request(path, options = {}) {
    const url = `${this.baseUrl}${path}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    }

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const contentType = response.headers.get('content-type')

      // Handle different response types
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json()

        if (data?.status) {
          if (data.status === 'success') {
            return data
          }

          if (data.status === 'fail') {
            const details =
              typeof data.data === 'string'
                ? data.data
                : JSON.stringify(data.data ?? {})
            throw new Error(details || 'Request failed')
          }

          if (data.status === 'error') {
            throw new Error(data.message || 'Server error')
          }
        }

        return data
      }

      // Non-JSON responses (e.g., proxied binary files)
      return response.url
    } catch (error) {
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('Network error - check if the server is running')
      }
      throw error
    }
  }

  // Configuration endpoints
  async getConfigs() {
    return this.request('/spectre-data/configs/')
  }

  async getConfigRaw(fileName) {
    return this.request(`/spectre-data/configs/${fileName}/raw`)
  }

  // Recording endpoints
  async recordSignal(payload) {
    return this.request('/recordings/signal', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  }

  async recordSpectrogram(payload) {
    return this.request('/recordings/spectrogram', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  }

  // Batch file endpoints
  async getBatchFiles(
    extensions = [],
    tags = [],
    year = null,
    month = null,
    day = null
  ) {
    const params = new URLSearchParams()

    extensions.forEach(ext => params.append('extension', ext))
    tags.forEach(tag => params.append('tag', tag))

    if (year) params.append('year', year)
    if (month) params.append('month', month)
    if (day) params.append('day', day)

    const queryString = params.toString()
    const path = `/spectre-data/batches/${queryString ? '?' + queryString : ''}`

    return this.request(path)
  }

  async getBatchFile(fileName) {
    // This returns the file URL for direct access
    return `${this.baseUrl}/spectre-data/batches/${fileName}`
  }

  async deleteBatchFile(fileName, dryRun = false) {
    const params = dryRun ? '?dry_run=true' : ''
    return this.request(`/spectre-data/batches/${fileName}${params}`, {
      method: 'DELETE'
    })
  }

  // Plot creation
  async createPlot(payload) {
    return this.request('/spectre-data/batches/plots', {
      method: 'PUT',
      body: JSON.stringify(payload)
    })
  }

  // Tag endpoints
  async getTags(year = null, month = null, day = null) {
    const params = new URLSearchParams()

    if (year) params.append('year', year)
    if (month) params.append('month', month)
    if (day) params.append('day', day)

    const queryString = params.toString()
    const path = `/spectre-data/batches/tags${queryString ? '?' + queryString : ''}`

    return this.request(path)
  }
}

// Create and export a singleton instance
export const apiClient = new ApiClient()

// Also export the class for testing or custom instances
export { ApiClient }
