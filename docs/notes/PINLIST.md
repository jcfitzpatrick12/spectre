# Pinned Features & Ideas

This document tracks feature ideas and enhancements that are planned for future iterations of the Spectre Web UI.

---

## High Priority - Future Iterations

### e-Callisto Network Integration
**Description**: Integration with the global e-Callisto solar radio observatory network

**Capabilities**:
- Download professionally-recorded solar radio spectrograms from 100+ stations worldwide
- Compare local amateur recordings with professional observatory data
- Access historical data by station, date, and time

**Backend Support**: Already implemented
- `GET /callisto/instrument-codes` - List all e-Callisto station codes
- `POST /callisto/batches` - Download FITS files from specific stations/dates

**User Value**:
- Educational: Compare amateur observations with professional data
- Validation: Verify local recordings against known sources
- Research: Access global solar event database

**Why Pinned**: Excellent feature for educational use and citizen science, but requires careful UX design for station/date selection. Defer until core data management is stable.

---

### Real-Time Waterfall Display
**Description**: Live spectrogram visualization during recording

**Capabilities**:
- Real-time frequency-time waterfall display while recording
- Visual feedback of signal reception quality
- Interactive monitoring for demonstrations

**User Value**:
- Educational demonstrations: "Watch radio signals appear in real-time"
- Troubleshooting: Immediately see if antenna/configuration is working
- Engagement: More interactive than waiting for post-processing

**Technical Considerations**:
- Requires WebSocket or Server-Sent Events for streaming
- Frontend canvas/WebGL rendering for performance
- Backend streaming of spectrogram chunks during recording

**Why Pinned**: Requires significant architectural changes (real-time data streaming). Focus on post-processing workflow first, then add live features.

---

## Medium Priority - Nice to Have

### Storage Usage Indicator
**Description**: Display total disk space used by recordings

**Implementation**:
- Badge or stat showing total storage used
- Count of total recordings
- Optional: Per-tag storage breakdown

**User Value**: Helps users know when to clean up old recordings

**Effort**: Low - simple aggregation of file sizes

---

### Tag Management Helper
**Description**: Better tag organization and discovery

**Capabilities**:
- View all existing tags with recording counts
- Tag suggestions when creating new recordings (autocomplete)
- Consistent tagging to avoid duplicates (e.g., "solar" vs "Solar" vs "sun")

**Backend Support**: Already implemented
- `GET /spectre-data/batches/tags` - Returns all unique tags

**User Value**: Maintain organized recording library, avoid tag proliferation

**Effort**: Low-Medium - UI for tag display and autocomplete component

---

### Advanced Plot Customization
**Description**: Expose additional plot parameters for power users

**Capabilities** (behind "Advanced Options" toggle):
- Frequency range sliders (`lower_freq`, `upper_freq`) - Zoom into specific bands
- Logarithmic scale toggle (`log_norm`) - Better dynamic range for weak signals
- dB above background mode (`dBb`) - Normalize relative to noise floor
- Custom colormap range (`vmin`, `vmax`) - Manual contrast control
- Multi-recording overlay - Compare multiple observations on one plot

**Backend Support**: Already implemented
- `PUT /spectre-data/batches/plots` - Supports all parameters

**User Value**:
- Better visualization of weak signals
- Band-specific analysis (e.g., focus on FM frequencies only)
- Comparison of different time periods

**Effort**: Medium - Multiple UI controls, form validation, preview functionality

**Why Pinned**: Good fit for "advanced options" pattern already established. Defer until basic features are solid.

---

## Low Priority - Future Consideration

### Raw Signal Recording Mode
**Description**: Record I/Q signal data without spectrogram processing

**Backend Support**: Already implemented
- `POST /recordings/signal` - Record raw signal data

**User Value**: Advanced users can post-process with different parameters or export to other software

**Why Pinned**: Advanced feature for power users, not aligned with "lightweight UI" goal for amateur/educational use

---

### Analytical Testing UI
**Description**: UI for validating signal generator recordings

**Backend Support**: Already implemented
- `GET /spectre-data/batches/<file_name>/analytical-test-results`

**User Value**: System calibration, quality assurance, debugging

**Why Pinned**: Developer/testing feature, not relevant for end users

---

## Notes

- This list is maintained as features are discovered or requested
- Items may be promoted/demoted in priority based on user feedback
- Check backend API documentation for implementation details: Backend API routes defined in `backend/src/spectre_server/routes/`

**Last Updated**: 2025-11-23
