class ApiClient {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl
  }

  async request(path, options = {}) {
    const url = `${this.baseUrl}${path}`

    // Handle timeout with AbortController if specified
    let timeoutId
    const controller = new AbortController()

    if (options.timeout) {
      timeoutId = setTimeout(() => controller.abort(), options.timeout)
    }

    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      signal: controller.signal,
      ...options
    }

    // Remove timeout from config (it's not a fetch option)
    delete config.timeout

    try {
      const response = await fetch(url, config)

      // Clear timeout if request completes
      if (timeoutId) clearTimeout(timeoutId)

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
      // Clear timeout on error
      if (timeoutId) clearTimeout(timeoutId)

      if (error.name === 'AbortError') {
        throw new Error('Request timeout - operation took too long')
      }
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

  async createConfig(fileName, payload) {
    return this.request(`/spectre-data/configs/${fileName}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    })
  }

  async updateConfig(fileName, payload) {
    return this.request(`/spectre-data/configs/${fileName}`, {
      method: 'PATCH',
      body: JSON.stringify(payload)
    })
  }

  async deleteConfig(fileName, dryRun = false) {
    const params = dryRun ? '?dry_run=true' : ''
    return this.request(`/spectre-data/configs/${fileName}${params}`, {
      method: 'DELETE'
    })
  }

  // Receiver endpoints
  async getReceivers() {
    return this.request('/receivers')
  }

  async getReceiverModes(receiverName) {
    return this.request(`/receivers/${receiverName}/modes`)
  }

  async getReceiverModel(receiverName, receiverMode) {
    const params = new URLSearchParams({ receiver_mode: receiverMode })
    return this.request(`/receivers/${receiverName}/model?${params}`)
  }

  // Recording endpoints
  // Extended timeout for long recordings (15 minutes = 900,000ms)
  async recordSignal(payload) {
    return this.request('/recordings/signal', {
      method: 'POST',
      body: JSON.stringify(payload),
      timeout: 900000  // 15 minutes
    })
  }

  async recordSpectrogram(payload) {
    return this.request('/recordings/spectrogram', {
      method: 'POST',
      body: JSON.stringify(payload),
      timeout: 900000  // 15 minutes
    })
  }

  // Batch file endpoints
  async getBatchFiles(
    extensions = [],
    tags = [],
    year = null,
    month = null,
    day = null,
    page = 1,
    perPage = 9,
    sort = 'desc'
  ) {
    const params = new URLSearchParams()

    extensions.forEach(ext => params.append('extension', ext))
    tags.forEach(tag => params.append('tag', tag))

    if (year) params.append('year', year)
    if (month) params.append('month', month)
    if (day) params.append('day', day)

    params.append('page', page)
    params.append('per_page', perPage)
    params.append('sort', sort)

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

  // Log endpoints
  async getLogs(processType = null, year = null, month = null, day = null) {
    const params = new URLSearchParams()

    if (processType) params.append('process_type', processType)
    if (year) params.append('year', year)
    if (month) params.append('month', month)
    if (day) params.append('day', day)

    const queryString = params.toString()
    const path = `/spectre-data/logs/${queryString ? '?' + queryString : ''}`

    return this.request(path)
  }

  async getLogContent(fileName) {
    return this.request(`/spectre-data/logs/${fileName}/raw`)
  }

  async pruneLogs(days, dryRun = false) {
    return this.request('/spectre-data/logs/prune', {
      method: 'POST',
      body: JSON.stringify({ days, dry_run: dryRun })
    })
  }
}

// Create and export a singleton instance
export const apiClient = new ApiClient()

// Also export the class for testing or custom instances
export { ApiClient }
