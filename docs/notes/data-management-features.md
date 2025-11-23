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
- **Rationale**: [TO BE FILLED DURING IMPLEMENTATION]
- **Alternative Considered**: Optimistic update (immediate UI removal) - rejected because [TO BE FILLED]

### Implementation Details

#### Backend API Integration
[TO BE FILLED DURING IMPLEMENTATION]

**Endpoint**: `DELETE /spectre-data/batches/<file_name>`

**API Client Method**:
```javascript
// Code snippets to be added during implementation
```

**Error Handling**:
- [TO BE FILLED]

#### Frontend Component Changes
[TO BE FILLED DURING IMPLEMENTATION]

**Component**: `SavedSpectrograms.jsx`

**Key Changes**:
- [TO BE FILLED]

**State Management**:
- [TO BE FILLED]

### Common Pitfalls & Solutions

**Pitfall 1**: [TO BE FILLED DURING IMPLEMENTATION]
- **Problem**: [TO BE FILLED]
- **Solution**: [TO BE FILLED]

### Testing Approach
[TO BE FILLED DURING IMPLEMENTATION]

- [ ] Delete succeeds and gallery refreshes
- [ ] Delete with non-existent file shows error
- [ ] Confirmation dialog can be cancelled
- [ ] Multiple rapid deletes handled gracefully

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
