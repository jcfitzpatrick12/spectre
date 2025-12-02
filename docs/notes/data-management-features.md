# Data Management Features Implementation Guide

**Target Audience**: Mid-level developers with basic React/Flask experience
**Implementation Date**: 2025-11-23
**Features**: Delete, Filtering, Log Viewer

---

## Overview

This guide documents the implementation of three essential data management features for the Spectre Web UI:

1. **Delete Function**: Remove individual spectrograms from the gallery
2. **Date & Tag Filtering**: Search and filter recordings by date and tag
3. **Log Viewer**: View system logs for troubleshooting

These features address workflow and data management needs for amateur radio operators and educational users.

---

## Architecture Context

### Frontend Stack
- **Framework**: React 18 with Vite
- **Styling**: CSS with dark mode support
- **State Management**: React hooks (useState, useEffect)
- **API Client**: Custom fetch-based client with timeout support (`frontend/src/api/spectreApiClient.js`)
- **Response Format**: JSend standard (success/fail/error)

### Backend Stack
- **Framework**: Flask REST API
- **Routes**: Defined in `backend/src/spectre_server/routes/`
- **Data Storage**: File-based with hierarchical directory structure (`YYYY/MM/DD/tag/`)

### Key Files
- API Client: `frontend/src/api/spectreApiClient.js`
- Gallery Component: `frontend/src/components/SavedSpectrograms.jsx`
- Main App: `frontend/src/App.jsx`

---

## Feature 1: Delete Function

### Problem Statement
Users accumulate recordings over time and need a simple way to remove unwanted spectrograms without accessing the command line. This is especially important for educational settings where users may not have terminal access.

### Architecture Decisions

**Decision 1: Confirmation Dialog Pattern**
- **Choice**: Modal confirmation dialog with filename display
- **Rationale**: Prevents accidental deletion of valuable data. Filename display helps users verify they're deleting the correct file.
- **Alternative Considered**: Undo functionality - rejected as overly complex for v1

**Decision 2: State Update Strategy**
- **Choice**: Pessimistic update (wait for API success before removing from UI)
- **Rationale**: Data integrity is more important than UI responsiveness. If the server deletion fails (network issue, permissions, file in use), showing the file as deleted would be misleading. Users can retry from the error state.
- **Alternative Considered**: Optimistic update (immediate UI removal) - rejected because it creates confusion if deletion fails, and recordings are valuable data that shouldn't appear to vanish without confirmation.

### Implementation Details

#### Backend API Integration

**Endpoint**: `DELETE /spectre-data/batches/<file_name>`

The API client already included a `deleteBatchFile` method (line 172-177 in `apiClient.js`):

**API Client Method**:
```javascript
async deleteBatchFile(fileName, dryRun = false) {
  const params = dryRun ? '?dry_run=true' : ''
  return this.request(`/spectre-data/batches/${fileName}${params}`, {
    method: 'DELETE'
  })
}
```

**Key Points**:
- `fileName` must be the exact filename (e.g., `20250122_143052_callisto.png`)
- Supports optional `dryRun` parameter for preview mode (not used in UI)
- Returns JSend response: `{status: 'success', data: null}` on success
- Throws error with message on failure

**Error Handling**:
- Network errors caught and displayed to user with "Failed to delete recording" message
- Non-existent files return HTTP 404, handled by API client as error
- Error state preserves confirmation dialog so user can retry or cancel

#### Frontend Component Changes

**Component**: `SavedSpectrograms.jsx`

**New State Variables** (lines 11-13):
```javascript
// Delete confirmation dialog state: {url, filename} or null
const [deleteConfirm, setDeleteConfirm] = useState(null)
const [deleting, setDeleting] = useState(false)  // Loading state during delete operation
```

**Handler Functions Added**:

1. **`handleDeleteClick(url)`** (lines 129-132): Triggered when user clicks delete button
   - Extracts filename from URL
   - Opens confirmation dialog with file details

2. **`handleDeleteConfirm()`** (lines 135-161): Executes deletion after confirmation
   - Sets `deleting` state to show loading indicator
   - Calls `apiClient.deleteBatchFile(filename)`
   - On success: Removes from local state, closes lightbox if needed, closes dialog
   - On failure: Displays error message, keeps dialog open for retry
   - Uses pessimistic update pattern (waits for API success)

3. **`handleDeleteCancel()`** (lines 164-166): Closes confirmation dialog

**UI Changes**:

1. **Recording Card Actions** (lines 244-265):
   - Wrapped download button in new `.recording-actions` div
   - Added delete button with trash icon (🗑)
   - Both buttons side-by-side with equal flex width

2. **Confirmation Dialog** (lines 305-336):
   - Modal overlay (click outside to cancel)
   - Shows filename in monospace font
   - Warning text: "This action cannot be undone"
   - Cancel and Delete buttons
   - Delete button disabled during deletion with "Deleting..." text
   - Similar pattern to existing lightbox modal

**State Management Flow**:
1. User clicks delete → `deleteConfirm` set to `{url, filename}`
2. Dialog renders conditionally when `deleteConfirm` is not null
3. User confirms → `deleting` set to true, API call made
4. Success → Update `recordings` array (filter out deleted item), reset states
5. Failure → Show error, keep dialog open, user can retry or cancel

### Common Pitfalls & Solutions

**Pitfall 1: Race Condition with Lightbox**
- **Problem**: If user has a file open in lightbox and deletes it, the lightbox stays open showing a broken image URL.
- **Solution**: Check if `lightboxUrl` matches the deleted URL and close lightbox if needed (line 149-151).

**Pitfall 2: Rapid Multiple Deletes**
- **Problem**: User could click delete on multiple files quickly, opening multiple dialogs or corrupting state.
- **Solution**: Only one confirmation dialog can be open at a time (state holds single object, not array). Subsequent clicks replace the dialog. The `deleting` state disables buttons during operation.

**Pitfall 3: Filename Extraction Consistency**
- **Problem**: URL parsing logic must match between different parts of the component.
- **Solution**: Use consistent `.split('/').pop()` pattern everywhere (lines 101, 130, throughout component). Consider refactoring to utility function if needed in more places.

**Pitfall 4: Error Display Location**
- **Problem**: Where should delete errors appear? Global error vs dialog-specific?
- **Solution**: Currently sets component-level `error` state which displays at top of section. This works but could be improved with toast notifications for better UX. For v1, keeping it simple.

### Testing Approach

**Manual Testing Checklist**:
- [x] Delete button appears on each recording card
- [x] Clicking delete shows confirmation dialog with correct filename
- [x] Cancel button closes dialog without deletion
- [x] Click outside dialog closes it (cancel behavior)
- [x] Confirm button triggers deletion
- [x] "Deleting..." state shows during operation
- [x] Successful deletion removes card from gallery
- [x] Error handling displays message if deletion fails
- [x] Lightbox closes if deleted file was open in it
- [x] Buttons disabled during deletion prevents double-submit
- [x] UI works in both light and dark modes
- [x] Responsive design works on mobile (buttons stack vertically)

**Test Cases for User**:
1. **Basic delete**: Create a test recording, delete it, verify it's removed
2. **Cancel delete**: Click delete, then cancel, verify recording remains
3. **Error handling**: Stop backend container, try delete, verify error message appears
4. **Lightbox interaction**: Open recording in lightbox, delete it, verify lightbox closes
5. **Mobile responsive**: Test on narrow viewport, verify buttons and modal layout

---

## Feature 2: Date & Tag Filtering

### Problem Statement
As recording collections grow, users need to quickly find specific observations. Filtering by date (e.g., "Show March solar observations") and tag (e.g., "Show all meteor scatter recordings") dramatically improves workflow efficiency.

### Architecture Decisions

**Decision 1: Collapsible Filter Panel**
- **Choice**: Hide/show filter controls with toggle button
- **Rationale**: Keeps UI clean by default for casual users, but power users can expand to access filters. Badge indicator shows when filters are active even when panel is collapsed.
- **Alternative Considered**: Always-visible filters - rejected because it adds visual clutter and takes vertical space away from gallery

**Decision 2: Explicit "Apply" Button**
- **Choice**: Changes to filter inputs don't immediately trigger reload - user must click "Apply Filters"
- **Rationale**: Prevents excessive API calls as user types or adjusts multiple fields. Users can set year, month, and tags together, then apply once.
- **Alternative Considered**: Auto-apply on change - rejected due to performance concerns with large datasets

**Decision 3: Separate Year/Month/Day Inputs**
- **Choice**: Three separate number inputs instead of date picker
- **Rationale**: Allows partial date filtering (e.g., "all of March 2025" without specifying day). Date pickers typically require full date selection.
- **Alternative Considered**: Single date picker - rejected because it doesn't support partial dates

### Implementation Details

#### Backend API Integration

**Endpoint**: `GET /spectre-data/batches/` with query parameters

The API client's `getBatchFiles` method already supported filtering (lines 145-165 in `apiClient.js`):

```javascript
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
```

**New API Method Used**:
```javascript
async getTags(year = null, month = null, day = null) {
  // Returns list of all unique tags in recordings
  // Used to populate filter dropdown
}
```

**Supported Filters**:
- `year`, `month`, `day` - Date filtering (all optional, can use any combination)
- `tags` - Array of tag names (supports multiple selection)
- Always filters to PNG extension for gallery display

#### Frontend Component Changes

**New State Variables** (lines 14-22):
```javascript
// Filter values
const [filters, setFilters] = useState({
  year: '',
  month: '',
  day: '',
  tags: []
})
const [availableTags, setAvailableTags] = useState([])  // Tags for dropdown
const [showFilters, setShowFilters] = useState(false)   // Panel visibility
```

**Key Functions Added**:

1. **`loadAvailableTags()`** (lines 30-38): Called on mount
   - Fetches all unique tags from backend
   - Populates dropdown options
   - Non-critical failure (logs warning but doesn't block UI)

2. **`loadRecordings(filterParams)`** (lines 40-62): Modified to accept filters
   - Accepts optional filter parameters
   - Falls back to current state if not provided
   - Builds query parameters from filter values
   - Empty strings treated as null (no filter)

3. **`handleApplyFilters()`** (lines 76-78): Apply button handler
   - Passes current filter state to `loadRecordings`
   - Triggers gallery refresh with filters

4. **`handleClearFilters()`** (lines 81-89): Clear button handler
   - Resets all filter state to empty values
   - Immediately reloads with no filters (shows all recordings)

5. **`hasActiveFilters()`** (lines 92-95): Check if filtering is active
   - Used to show/hide badge indicator
   - Used to enable/disable clear button

6. **`handleTagChange(e)`** (lines 98-101): Multi-select handler
   - Extracts selected values from multi-select element
   - Updates tags array in filter state

#### Frontend UI Design

**Filter Toggle Button** (lines 251-258):
- Appears in gallery controls header
- Shows "🔼 Show Filters" or "🔽 Hide Filters"
- Badge (●) pulses when filters are active
- Consistent styling with other control buttons

**Filters Panel** (lines 277-368): Collapsible section
- Background color matches tertiary theme
- Grid layout: 4 columns on desktop, single column on mobile
- Appears below header when `showFilters` is true

**Date Inputs** (lines 280-317):
- Year: 4-digit number (2020-2099)
- Month: 1-12
- Day: 1-31
- HTML5 number inputs with min/max validation
- Placeholders provide guidance

**Tag Multi-Select** (lines 319-337):
- Grid column span 2 (takes more space)
- Shows all available tags from `availableTags` state
- size="3" shows 3 options at once
- Multiple selection enabled
- Hint text: "Hold Ctrl/Cmd to select multiple"
- Falls back to "No tags available" if none exist

**Action Buttons** (lines 340-354):
- Apply Filters: Primary action (purple theme color)
- Clear Filters: Secondary action (gray), disabled when no filters active
- Equal width flex layout
- Stack vertically on mobile

**Active Filter Pills** (lines 356-366):
- Only shown when filters are active
- Displays each active filter as a pill badge
- Visual feedback of what's being filtered
- Example: "Year: 2025", "Month: 3", "Tag: solar"

### Common Pitfalls & Solutions

**Pitfall 1: Empty String vs Null Confusion**
- **Problem**: Empty string `""` from cleared input is not the same as `null` for API. Could cause filtering issues.
- **Solution**: API client checks for truthy values before adding to query params (lines 52-54 in updated component). Empty strings are falsy and get treated as null.

**Pitfall 2: Stale Tag List**
- **Problem**: If user creates a new recording with a new tag, it won't appear in filter dropdown until page refresh.
- **Solution**: Could add refresh button for tags, or reload tags after recording completes. For v1, acceptable to require manual refresh since tag creation is infrequent.

**Pitfall 3: Invalid Date Combinations**
- **Problem**: User could enter February 31st or Month 13, which are invalid.
- **Solution**: HTML5 input validation with min/max attributes prevents out-of-range values. Backend should also validate. Invalid combinations (e.g., Feb 31) will return no results but won't crash.

**Pitfall 4: Multi-Select UX Confusion**
- **Problem**: Users unfamiliar with multi-select may not know to hold Ctrl/Cmd.
- **Solution**: Hint text below select element explains interaction. Consider future enhancement with checkbox list or tag-style selector.

**Pitfall 5: Filter State Persistence**
- **Problem**: Applying filters, then refreshing page loses filter state.
- **Solution**: For v1, this is acceptable. Future enhancement: store filters in URL query params or localStorage for persistence across page loads.

### Testing Approach

**Manual Testing Checklist**:
- [x] Filter toggle button shows/hides panel
- [x] Badge appears on toggle when filters are active
- [x] Year-only filter works (e.g., all 2025 recordings)
- [x] Month-only filter works
- [x] Full date filter works (year + month + day)
- [x] Single tag filter works
- [x] Multiple tag filter works
- [x] Combined date and tag filters work together
- [x] Apply button triggers reload with filters
- [x] Clear button resets filters and reloads all recordings
- [x] Clear button disabled when no filters active
- [x] Active filter pills display correctly
- [x] Tag dropdown populates from backend
- [x] Empty results show appropriate message
- [x] Responsive layout works on mobile
- [x] Filter panel works in dark mode

**Test Cases for User**:
1. **Year filter**: Filter to specific year, verify only that year shown
2. **Month range**: Filter to year + month (e.g., March 2025), verify results
3. **Single tag**: Select one tag, verify filtered correctly
4. **Multiple tags**: Select multiple tags with Ctrl/Cmd, verify OR logic (shows recordings with any selected tag)
5. **Combined filters**: Year + month + tag together
6. **Clear filters**: After filtering, click clear, verify all recordings return
7. **No results**: Filter to non-existent date, verify "no recordings" message
8. **Panel persistence**: Apply filters, collapse panel, verify badge still shows and filters still active

---

## Feature 3: Log Viewer

### Problem Statement
When recordings fail or behave unexpectedly, users (especially in educational settings) need access to logs for troubleshooting without requiring terminal access or SSH into the server.

### Architecture Decisions

**Decision 1: Separate Component with Modal Viewer**
- **Choice**: Create dedicated LogViewer component with list + modal pattern
- **Rationale**: Logs are fundamentally different from recordings (text files vs images). Separate component keeps concerns isolated. Modal viewer handles potentially long log files better than inline display.
- **Alternative Considered**: Add logs to gallery as another file type - rejected because mixing logs and spectrograms in one UI would be confusing

**Decision 2: List-Then-View Pattern**
- **Choice**: Show list of log files first, click to view content in modal
- **Rationale**: Log files can be large (MB+). Loading all content upfront would be slow and wasteful. Users typically know which log file they need based on timestamp.
- **Alternative Considered**: Auto-load recent log - rejected because users need to choose which log based on when issue occurred

### Implementation Details

#### Backend API Integration

**New API Client Methods** (lines 201-218 in `apiClient.js`):

```javascript
async getLogs(processType = null, year = null, month = null, day = null) {
  // Returns list of log filenames with optional filtering
  const params = new URLSearchParams()
  if (processType) params.append('process_type', processType)
  // Date params also supported but not exposed in UI initially
  return this.request(`/spectre-data/logs/${queryString}`)
}

async getLogContent(fileName) {
  // Returns raw text content of specific log file
  return this.request(`/spectre-data/logs/${fileName}/raw`)
}
```

**Endpoints**:
- `GET /spectre-data/logs/` - List log files
  - Query param: `process_type` (worker/user)
  - Query params: `year`, `month`, `day` (date filtering, not yet used in UI)
- `GET /spectre-data/logs/<file_name>/raw` - Get log content as plain text
- `POST /spectre-data/logs/prune` - Delete logs older than N days (payload: `{ "days": number, "dry_run": bool }`)

**Client helper** (`apiClient.js`):

```javascript
async pruneLogs(days, dryRun = false) {
  return this.request('/spectre-data/logs/prune', {
    method: 'POST',
    body: JSON.stringify({ days, dry_run: dryRun })
  })
}
```

#### Component Structure

**New Component**: `LogViewer.jsx` (standalone, 175 lines)

**State Management**:
```javascript
const [logFiles, setLogFiles] = useState([])          // List of log filenames
const [selectedLog, setSelectedLog] = useState(null)   // Currently viewing log
const [logContent, setLogContent] = useState(null)     // Text content of selected log
const [processTypeFilter, setProcessTypeFilter] = useState('')  // Filter value
const [loading, setLoading] = useState(true)           // Initial list load
const [loadingContent, setLoadingContent] = useState(false)  // Individual log load
```

**Key Functions**:

1. **`loadLogs()`** (lines 17-30): Fetch log file list
   - Triggers on mount and when filter changes
   - Passes `processTypeFilter` to API
   - Updates `logFiles` array

2. **`handleLogClick(fileName)`** (lines 33-46): View specific log
   - Sets `selectedLog` to show modal
   - Fetches content via `getLogContent`
   - Shows loading state during fetch

3. **`handleDownload(fileName)`** (lines 57-67): Download log as text file
   - Creates Blob from `logContent`
   - Triggers browser download with original filename

#### UI Design

**Main Section** (lines 77-132):
- Header with "System Logs" title
- Process type filter dropdown (All/Worker/User)
- Refresh button + destructive "🧹 Prune Logs" action
- Success banner confirming prune actions (dismissable)
- List of log files with filename + View button

**Log List Items** (lines 114-126):
- Filename in monospace font (shows timestamp/type info)
- "👁 View" button to open modal
- Hover effect for interactivity

**Log Content Modal** (lines 134-177):
- Full-screen overlay (click outside to close)
- Header: Filename + close button
- Body: Scrollable `<pre>` element with log text
- Footer: Download and Close buttons
- Monospace font for proper log formatting

#### Understanding Log Types

Spectre generates two types of logs:

**Worker Logs**:
- Background process logs from spectrogram/signal recording workers
- Show FFT processing, GNU Radio flowgraph execution, file I/O
- Useful for: Debugging recording failures, hardware issues, processing errors
- Example issues: SDR device not found, sample rate errors, disk space

**User Logs**:
- API request logs, user-initiated actions
- Show HTTP requests, configuration changes, validation errors
- Useful for: Debugging Web UI issues, API errors, invalid configurations
- Example issues: Config syntax errors, missing parameters, permission issues

#### Pagination Implementation

**Problem**: With many log files accumulating over time, the log list can grow very long, leading to excessive scrolling and poor UX.

**Solution**: Client-side pagination limiting display to 5 logs per page, consistent with the gallery pagination pattern.

**State Variables** (lines 12-15):
```javascript
const [currentPage, setCurrentPage] = useState(1)
const [allLogs, setAllLogs] = useState([])  // Complete log list for pagination
const logsPerPage = 5
```

**Implementation Strategy**:
- **Client-Side Pagination**: Backend doesn't support paginated log endpoints, so all logs are fetched once and sliced client-side
- **Page Size**: 5 logs per page (prevents long scrolling while showing enough content)
- **Consistency**: Matches pagination pattern from SavedSpectrograms gallery

**Key Functions**:

1. **`updatePaginatedLogs(logs, page)`** (lines 44-51): Slice logs for current page
   - Calculates start/end indices based on page number
   - Updates `logFiles` with paginated subset
   - Updates `currentPage` state

2. **`getPaginationMetadata()`** (lines 53-61): Calculate pagination info
   - Returns: `totalLogs`, `totalPages`, `hasPrev`, `hasNext`
   - Used by UI to enable/disable navigation buttons

3. **`handleNextPage()`** and **`handlePrevPage()`** (lines 98-113): Navigation
   - Check if next/prev page exists before navigating
   - Call `updatePaginatedLogs` with new page number

**UI Controls** (lines 175-200):
- Previous/Next buttons with arrow symbols
- Page info: "Page X of Y (Z total)"
- Buttons disabled when at first/last page
- Only shown when totalPages > 1
- Shares the pagination control styling used by SavedSpectrograms (consistency)

#### Prune Logs Workflow

**Problem**: Log folders grow without bound on long-running installs. Users need a quick way to delete aged log files without shell access.

**Solution**: Add a destructive "Prune Logs" CTA inside LogViewer that calls the new backend endpoint.

**Flow**:
1. User clicks 🧹 button → opens modal asking "Days to keep" (default 30, accepts `0` to nuke everything)
2. Frontend validates integer ≥ 0 and blocks confirm while invalid or request in-flight
3. API returns `{ deleted: n }`; UI shows dismissable success banner and reloads log listing
4. Errors stay inside the modal via `modal-warning`, giving user a chance to adjust input and retry

**State hooks**:
```javascript
const [showPruneModal, setShowPruneModal] = useState(false)
const [pruneDays, setPruneDays] = useState(30)
const [pruning, setPruning] = useState(false)
const [pruneError, setPruneError] = useState(null)
const [statusMessage, setStatusMessage] = useState(null)
```

**Backend behavior**:
- Service walks every log path returned by `get_logs([], None, None, None)` and deletes files older than `(now - days)` based on mtime
- Supports optional `dry_run` for future CLI reuse
- Returns the absolute paths deleted; route summarizes as `{ deleted, days, dry_run }`

**Filter Integration** (lines 17-20):
- When process type filter changes, reset to page 1
- Ensures user sees results from the beginning after filtering

### Common Pitfalls & Solutions

**Pitfall 1: Large Log Files Blocking UI**
- **Problem**: Multi-MB log files could freeze browser when loaded into modal
- **Solution**: Content loaded on-demand (not preloaded). Modal body is scrollable with overflow. Browser handles large text content reasonably well in `<pre>` tags. Future enhancement: pagination or streaming.

**Pitfall 2: Log Filename Parsing**
- **Problem**: Log filenames may vary in format, making display inconsistent
- **Solution**: Display raw filename without parsing. Filenames are already meaningful (timestamp-based). No need to parse - keep it simple and reliable.

**Pitfall 3: Download Filename Collision**
- **Problem**: Downloading multiple logs could overwrite each other if using generic name
- **Solution**: Use original log filename for download (`link.download = fileName`). Browser automatically handles naming if file exists.

**Pitfall 4: Modal Not Closing on Error**
- **Problem**: If log content fails to load, modal stays open with error, no way to close except close button
- **Solution**: Error handling keeps modal open so user can retry or see error message. Close button always available. This is acceptable UX for debugging tool.

### Testing Approach

**Manual Testing Checklist**:
- [x] Log list loads on component mount
- [x] Process type filter (All/Worker/User) works correctly
- [x] Refresh button reloads log list
- [x] Clicking "View" opens modal with log content
- [x] Modal shows loading state while fetching content
- [x] Log content displays in monospace font
- [x] Long logs are scrollable in modal
- [x] Download button saves log as text file with correct filename
- [x] Close button and overlay click both close modal
- [x] Error handling displays when log fetch fails
- [x] Empty state shows "No log files" message
- [x] Responsive layout works on mobile
- [x] Dark mode styling applied correctly

**Test Cases for User**:
1. **View logs**: Click View on any log, verify content appears
2. **Filter by type**: Change process type filter, verify list updates
3. **Download log**: Click Download in modal, verify file downloads
4. **Long log scrolling**: View a large log file, verify scrolling works
5. **Mobile responsive**: Test on narrow viewport, verify layout adapts
6. **Dark mode**: Toggle dark mode, verify log viewer follows theme

---

## Common Patterns Established

### Pattern 1: API Client Extension
[TO BE FILLED AT END OF IMPLEMENTATION]

When adding new backend endpoints to the frontend:
1. [TO BE FILLED]

### Pattern 2: Error Handling
[TO BE FILLED AT END OF IMPLEMENTATION]

Standard error handling approach:
1. [TO BE FILLED]

### Pattern 3: Loading States
[TO BE FILLED AT END OF IMPLEMENTATION]

How we handle async operations:
1. [TO BE FILLED]

---

## Lessons Learned

[TO BE FILLED AT END OF IMPLEMENTATION]

### What Went Well
- [TO BE FILLED]

### Challenges Faced
- [TO BE FILLED]

### Future Improvements
- [TO BE FILLED]

---

## Next Steps for Future Developers

[TO BE FILLED AT END OF IMPLEMENTATION]

If you're adding similar features:
1. [TO BE FILLED]

---

## References

- Backend API: Check route files in `backend/src/spectre_server/routes/`
- JSend Specification: https://github.com/omniti-labs/jsend
- React Hooks: https://react.dev/reference/react
- Dark Mode Implementation: See `frontend/src/App.jsx` and `frontend/src/styles/main.css`

---

**Document Status**: Work in Progress - Will be completed as features are implemented
**Last Updated**: 2025-11-23
