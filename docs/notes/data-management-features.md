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

**Decision 1**: [TO BE FILLED DURING IMPLEMENTATION]
- **Choice**: [TO BE FILLED]
- **Rationale**: [TO BE FILLED]

### Implementation Details
[TO BE FILLED DURING IMPLEMENTATION]

#### Backend API Integration

**Endpoint**: `GET /spectre-data/batches/` with query parameters

**Supported Filters**:
- `year`, `month`, `day` - Date filtering
- `tag` - Tag filtering (supports multiple)

#### Frontend UI Design
[TO BE FILLED DURING IMPLEMENTATION]

### Common Pitfalls & Solutions
[TO BE FILLED DURING IMPLEMENTATION]

### Testing Approach
[TO BE FILLED DURING IMPLEMENTATION]

---

## Feature 3: Log Viewer

### Problem Statement
When recordings fail or behave unexpectedly, users (especially in educational settings) need access to logs for troubleshooting without requiring terminal access or SSH into the server.

### Architecture Decisions

**Decision 1**: [TO BE FILLED DURING IMPLEMENTATION]
- **Choice**: [TO BE FILLED]
- **Rationale**: [TO BE FILLED]

### Implementation Details
[TO BE FILLED DURING IMPLEMENTATION]

#### Backend API Integration

**Endpoints**:
- `GET /spectre-data/logs/` - List log files
- `GET /spectre-data/logs/<file_name>/raw` - Get log content

**Filters**:
- `process_type` - Filter by worker/user logs

#### Understanding Log Types
[TO BE FILLED DURING IMPLEMENTATION]

**Worker Logs**: [TO BE FILLED]
**User Logs**: [TO BE FILLED]

### Common Pitfalls & Solutions
[TO BE FILLED DURING IMPLEMENTATION]

### Testing Approach
[TO BE FILLED DURING IMPLEMENTATION]

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
