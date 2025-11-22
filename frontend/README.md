# Spectre Web UI

A modern browser-based interface for recording and visualizing radio spectrograms using the Spectre system. Built with React and designed for amateur radio enthusiasts.

## Overview

The Spectre Web UI provides a local-only interface for:
- **Recording spectrograms** - Configure and start new recordings with customizable parameters
- **Viewing saved recordings** - Browse, preview, and download previously captured spectrograms
- **Managing configurations** - Select from available receiver configurations

**Important:** This web interface is designed for **local use only**. It runs on your own machine via Docker and is not intended for remote access or deployment.

## Browser Compatibility

### Required
- **Firefox** (latest version) - Primary development and testing browser

### Supported
- **Chrome/Chromium** (latest version)
- **Safari** (latest version)

## Development Setup

### Prerequisites

- Docker and Docker Compose installed
- Node.js 18+ (for local development without Docker)
- Git

### Quick Start with Docker

1. **Clone the repository:**
   ```bash
   cd /path/to/spectre
   ```

2. **Start the development stack:**
   ```bash
   docker compose -f docker-compose.dev.yml up
   ```

3. **Access the Web UI:**
   - Open your browser to: http://localhost:3000
   - The backend API is available at: http://localhost:5001

4. **Stop the stack:**
   ```bash
   docker compose -f docker-compose.dev.yml down
   ```

### Development Stack Architecture

The `docker-compose.dev.yml` stack includes three services:

- **spectre-dev-server** (port 5001) - Flask backend API serving spectrogram data
- **spectre-dev-cli** - Command-line interface for backend configuration
- **spectre-frontend** (port 3000) - Vite development server with hot module reload

All services communicate via the `spectre-dev-network` Docker network. The frontend automatically proxies API requests to the backend:
- `/recordings/*` → `http://spectre-dev-server:5001`
- `/spectre-data/*` → `http://spectre-dev-server:5001`

### File Storage

Spectrogram PNG files are stored in the Docker volume `spectre-dev-data` at the container path `/app/.spectre-data`. The directory structure is:

```
.spectre-data/
└── batches/
    └── YYYY/
        └── MM/
            └── DD/
                └── tag_name/
                    └── YYYYMMDD_HHMMSS_tag.png
```

For example: `.spectre-data/batches/2025/01/22/callisto/20250122_143052_callisto.png`

## Using the Web UI

### Starting a New Recording

1. **Select Configuration:** Choose a receiver configuration from the dropdown
2. **Set Frequency:** Enter the center frequency in MHz (e.g., `20.1` for 20.1 MHz)
3. **Set Duration:** Specify recording length in seconds
4. **Advanced Options (optional):**
   - Enable/disable automatic plotting
   - Configure chunks per spectrogram file
   - Adjust integration time
5. **Click "Start Recording"**
6. **Monitor Progress:** Watch the status as the recording and plotting complete
7. **View Result:** The new spectrogram appears inline after completion

### Viewing Saved Recordings

The "Previous Recordings" gallery displays all saved spectrogram PNGs from past recording sessions.

#### Features:

**Gallery Grid View:**
- Thumbnails arranged in a responsive grid (300px minimum width)
- Each card shows:
  - **Tag name** (receiver configuration, e.g., "callisto")
  - **Timestamp** (recording date and time)
  - **Filename** (original PNG filename)
  - **Download button** (⬇ Download)

**Refresh:**
- Click the **"↻ Refresh"** button in the gallery header to reload the list
- The gallery also auto-refreshes when a new recording completes

**Preview:**
- Click any thumbnail to view the full-size spectrogram in a lightbox overlay
- Click outside the lightbox or the × button to close
- Download directly from the lightbox view

**Download:**
- Click **"⬇ Download"** on any card to save the PNG file locally
- Files download with their original filename (e.g., `20250122_143052_callisto.png`)

#### Metadata Display:

The UI automatically parses metadata from filenames:
- **Filename format:** `YYYYMMDD_HHMMSS_tag.png`
- **Date/Time extraction:** Converts to readable format (`2025-01-22 14:30:52`)
- **Tag identification:** Displays the configuration name

If a filename doesn't match the expected format, the UI gracefully falls back to displaying "Unknown" for metadata fields.

#### Empty State:

If no recordings exist, the gallery displays: "No recordings yet. Start your first recording above!"

#### Error Handling:

If loading fails, an error message appears with a **"Retry"** button to attempt reloading.

## Local Development Workflow

### With VS Code Dev Containers

If using VS Code with the Remote-Containers extension:

1. Open the project folder in VS Code
2. Click "Reopen in Container" when prompted
3. The dev container automatically starts all services
4. Frontend is accessible at http://localhost:3000

### Without Docker (Local Node.js)

For faster iteration during frontend-only development:

1. **Start the backend separately:**
   ```bash
   docker compose -f docker-compose.dev.yml up spectre-dev-server
   ```

2. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

4. **Access at:** http://localhost:3000

The Vite dev server proxies API calls to `localhost:5001` automatically.

### Making Changes

**Hot Module Reload:**
- Edit any `.jsx`, `.js`, or `.css` file in `frontend/src/`
- Changes appear instantly in the browser (no page refresh needed)

**Adding Components:**
- Create new components in `frontend/src/components/`
- Follow the existing naming convention: `ComponentName.jsx`
- Import and use in parent components

**Styling:**
- All styles are in `frontend/src/styles/main.css`
- Uses standard CSS (no CSS-in-JS or preprocessors)
- Follow existing class naming patterns

**API Client:**
- Extend `frontend/src/services/apiClient.js` for new endpoints
- All methods return JSend-formatted responses:
  ```json
  {
    "status": "success" | "fail" | "error",
    "data": {...}
  }
  ```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── RecordingForm.jsx      # Form for starting recordings
│   │   └── SavedSpectrograms.jsx  # Gallery of saved PNGs
│   ├── services/
│   │   └── apiClient.js           # API communication layer
│   ├── styles/
│   │   └── main.css               # All application styles
│   ├── App.jsx                    # Main application component
│   └── main.jsx                   # Entry point
├── index.html                     # HTML template
├── vite.config.js                 # Vite configuration (proxy setup)
├── package.json                   # Dependencies
├── nginx.conf                     # Production nginx config
└── Dockerfile                     # Production build image
```

## Production Deployment

### Build Production Image

```bash
docker compose -f docker-compose.yml build spectre-frontend
```

### Run Production Stack

```bash
docker compose -f docker-compose.yml up
```

**Access at:** http://localhost:8080

The production build uses nginx to serve static files and proxy API requests to the backend.

## Troubleshooting

### "Network error - check if the server is running"

**Cause:** Frontend cannot connect to backend

**Solution:**
1. Verify backend is running: `docker ps | grep spectre-dev-server`
2. Check backend health: `curl http://localhost:5001/spectre-data/configs/`
3. Restart the stack: `docker compose -f docker-compose.dev.yml restart`

### "Failed to load recordings"

**Cause:** Backend returned an error or no PNG files exist

**Solution:**
1. Check if any recordings exist: `docker exec spectre-dev-server ls /app/.spectre-data/batches/`
2. Try the "Retry" button or "Refresh" button
3. Create a test recording to verify the workflow

### Images not displaying in gallery

**Cause:** Proxy configuration or CORS issue

**Solution:**
1. Verify Vite proxy in `vite.config.js`:
   ```javascript
   proxy: {
     '/spectre-data': 'http://spectre-dev-server:5001'
   }
   ```
2. Check browser console for errors
3. Ensure backend allows serving images: `curl http://localhost:5001/spectre-data/batches/<filename>`

### Hot reload not working

**Cause:** Volume mount or Vite watcher issue

**Solution:**
1. For Docker: Ensure volume mount in `docker-compose.dev.yml`: `./frontend:/app`
2. For local dev: Check file system permissions
3. Restart Vite: `docker compose -f docker-compose.dev.yml restart spectre-frontend`

## Additional Resources

- **Main Project README:** [/README.md](../README.md) - Overall project documentation
- **Backend API:** Check `backend/src/spectre_server/routes/` for endpoint definitions
- **CLI Commands:** See `cli/src/spectre_cli/commands/` for recording logic
- **GitHub Issues:** https://github.com/jcfitzpatrick12/spectre/issues

## Contributing

When making changes to the Web UI:

1. **Test on Firefox** (required) - Primary browser target
2. **Test on Chrome** (preferred) - Ensure broad compatibility
3. **Follow existing patterns** - Match component structure and styling
4. **Keep it simple** - Design for amateur radio users, avoid unnecessary complexity
5. **Local-only focus** - No authentication, remote access, or cloud features needed

## Future Enhancements

Potential features for future development (not yet implemented):

- **Date range filtering** - Filter recordings by date
- **Tag filtering** - Show recordings from specific configurations only
- **Sorting options** - Sort by date, tag, or filename
- **Search functionality** - Quick search by filename or tag
- **Batch operations** - Delete multiple recordings at once
- **Comparison view** - Side-by-side spectrogram comparison
- **Waterfall view** - Real-time waterfall display during recording
- **Export options** - Bulk download or archive creation
