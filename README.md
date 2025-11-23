<h1 align="center">
  Spectre: Process, Explore and Capture Transient Radio Emissions
</h1>

<div align="center">
  <img src="gallery/solar_radio.png" width="30%" hspace="5" alt="Solar Radio Observations">
  <img src="gallery/spectre.png" width="30%" hspace="5" alt="Spectre Logo">
  <img src="gallery/fm_radio.png" width="30%" hspace="5" alt="FM Band">
</div>

<div align="center">
  <img src="gallery/finland_comparison.png" width="45%" hspace="7" alt="Solar Radio Observations">
  <img src="gallery/solar_radio_narrowband.png" width="45%" hspace="7" alt="Solar Radio Observations">
</div>

## Getting started

Check out our [GitHub Wiki here](https://github.com/jcfitzpatrick12/spectre/wiki). Quick links are provided below:  

- [Installation](https://github.com/jcfitzpatrick12/spectre/wiki/Installation)
- [Tutorials](https://github.com/jcfitzpatrick12/spectre/wiki/Tutorials)
- [Contributing](https://github.com/jcfitzpatrick12/spectre/wiki/Contributing)

Track our progress and upcoming features on our [GitHub Project Board](https://github.com/users/jcfitzpatrick12/projects/3).

## About Us

_Spectre_ is a free and open source receiver-agnostic program for recording and visualising radio spectrograms. It's geared for hobbyists, citizen scientists, and academics who want to achieve scientifically interesting results at low cost. 

Powered by [GNU Radio](https://www.gnuradio.org/) and [FFTW](https://www.fftw.org/), it provides high performance on modest hardware. Applications include:  

- Solar and Jovian radio observations
- Educational outreach and citizen science
- Amateur radio experimentation
- Lightning and atmospheric event detection
- RFI monitoring

## **Features**

- Simple installation with Docker
- Wide receiver support (SDRplay, HackRF, RTL-SDR, USRP)
- Run natively on Linux, including Raspberry Pi
- Intuitive CLI tool
- Live record spectrograms and I/Q data  
- Offers fixed and sweeping center frequency modes
- Backend web server with a discoverable RESTful API
- **Web UI for local spectrogram recording and visualization**
- Developer-friendly and extensible

ℹ️ Looking for a lightweight alternative? Check out [_Spectrel_](https://github.com/jcfitzpatrick12/spectre-lite), a stripped-back derivative of _Spectre_, written in pure C. No Docker required.

## Web UI

Spectre ships with a lightweight browser UI for starting spectrogram recordings, monitoring progress, and reviewing PNG outputs, all without leaving your local machine.

### Local Web UI via `docker-compose.yml`

1. **Build once** (uses the existing backend + new frontend service in the same stack):
   ```bash
   docker compose build spectre-server spectre-frontend
   ```
2. **Start the services** (backend + nginx-hosted frontend + CLI helper):
   ```bash
   docker compose up spectre-server spectre-frontend spectre-cli
   ```
3. **Open your browser:** [http://localhost:8080](http://localhost:8080) serves the React UI. All API calls are proxied inside the Compose network to `spectre-server`, so no extra port wrangling is required.
4. **Stop everything:** press `Ctrl+C` in the compose terminal. Restart with the same `docker compose up` command whenever you need it.

This flow keeps the UI “in the family” with the backend container—no manual Docker commands beyond the two above.

### Development stack & VS Code Dev Containers

Prefer hot reload or editing inside the container?

1. Install the VS Code **Dev Containers** extension.
2. Run `Ctrl+Shift+P` → “Dev Containers: Reopen in Container”. VS Code will spin up the services from `docker-compose.dev.yml` (`spectre-dev-server`, `spectre-dev-cli`, `spectre-frontend` dev server).
3. Once the containers are online, visit [http://localhost:3000](http://localhost:3000) for the Vite dev server (it proxies API calls to `http://spectre-dev-server:5001` automatically).
4. To use the dev stack from the terminal only, run:
   ```bash
   docker compose -f docker-compose.dev.yml up --build
   ```

### Using the Web UI

- **Recording Form:** Select a receiver config tag (this encodes center frequency and hardware settings) and enter a duration in seconds. Optional advanced toggles mirror the CLI flags (`force_restart`, `max_restarts`, `validate`).
- **Status + Result:** The UI calls `POST /recordings/spectrogram` and, on success, immediately triggers `PUT /spectre-data/batches/plots` for the same tag/time window. When the PNG URL returns, it renders inline.
- **View Previous:** The “Previous Recordings” list pulls directly from `GET /spectre-data/batches?extension=png`, so every PNG served from `/spectre-data/batches/<file>.png` is one click away.
- **Client-side validation:** Duration must be numeric and positive (≤3600 s), restart limits stay within 1‑20, and you’ll get inline guidance before any network calls fire.

### Configuration

#### Default Profiles

On first startup, Spectre automatically seeds three default configuration profiles so the UI dropdown is never empty:

| Profile | Receiver | Hardware Required | Use Case | Description |
|---------|----------|-------------------|----------|-------------|
| **demo-sine** | signal_generator | ❌ No | Testing, UI demo | Virtual sine wave at 32 kHz - works anywhere without SDR hardware |
| **rtlsdr-fm-wide** | rtlsdr | ✅ RTL-SDR | FM broadcast monitoring | Wide-band FM at 98.5 MHz with 2.048 MSPS, optimized for RTL-SDR Blog v3 |
| **rtlsdr-solar-20MHz** | rtlsdr | ✅ RTL-SDR + upconverter | Solar/Jupiter monitoring | Long-duration capture at 20.1 MHz for natural radio sources |

These profiles are copied from `/app/default_profiles/` into `/app/.spectre-data/configs/` on container startup **only if they don't already exist**. This means:

- **Fresh install**: All three profiles appear automatically
- **Existing install**: Your modified configs are never overwritten
- **Selective deletion**: If you delete a default profile, it will be restored on next container restart

#### Custom Configurations

Create or inspect receiver configs via the CLI (inside whichever CLI container you're already running):

```bash
# Create a configuration for your SDR device
docker exec -it spectre-cli spectre create config --receiver rtlsdr --mode fixed --tag my_rtlsdr

# List available configurations
docker exec -it spectre-cli spectre get configs
```

> Replace `spectre-cli` with `spectre-dev-cli` when you are running the dev stack from `docker-compose.dev.yml`.

The UI reads `/spectre-data/configs/` and automatically offers every tag it finds. Use tags whose parameters already contain the center frequency / bandwidth you care about—no extra UI fields are needed today because the runtime API accepts tags + duration only.
