# __SPECTRE: Process, Explore and Capture Transient Radio Emissions__

## Overview

:loudspeaker: **This project is under active development. Contributors welcome.**  :loudspeaker:

`spectre` is a receiver-agnostic program for recording and visualising radio spectrograms. Powered by [GNU Radio](https://www.gnuradio.org/).

**Features**:  

- Intuitive CLI tool :computer:
- Wide receiver support :satellite:
- Live recording of radio spectrograms and I/Q data :floppy_disk:
- Flexible, configurable data capture :gear:
- Containerised backend :whale:
- Developer-friendly, extensible digital signal processing framework :hammer_and_wrench:

## Use-case: Solar Radio Observations :sunny:
Observations of the huge X9.0 solar flare on October 3rd 2024. A comparison of a ```spectre``` spectrogram (second panel) captured in the West End of Glasgow, to that observed by the [CALLISTO](https://e-callisto.org/) spectrometer stationed in Egypt, Alexandria (top panel)
![Observations of the huge X9.0 solar flare on October 3rd 2024. A comparison of a spectre spectrogram (second panel) captured in the West End of Glasgow, to that observed by the CALLISTO spectrometer stationed in Egypt, Alexandria (top panel)](docs/gallery/comparison.png)


## Supported Receivers

Initial support is focused on the SDRplay RSP* series via [`gr-sdrplay3`](https://github.com/fventuri/gr-sdrplay3). A wide range of receiver support is planned.

Current supported receivers include:  

- [RSP1A (from SDRPlay)](https://www.sdrplay.com/rsp1a/)
- [RSPduo (from SDRPlay)](https://www.sdrplay.com/rspduo/)

The framework is in place to integrate the following receivers, this is planned for the near future:  

- RSP1, RSP1B, RSP2, RSPdx (via [`gr-sdrplay3`](https://github.com/fventuri/gr-sdrplay3))
- USRP SDRs (e.g., the [b200-mini](https://www.ettus.com/all-products/usrp-b200mini/))
- RTLSDR, AirspyHF, BladeRF, HackRF, LimeSDR, PLUTO (via [`Soapy`](https://wiki.gnuradio.org/index.php/Soapy))

**Please note! SDRPlay clones (i.e. unofficially produced copies of SDRPlay receivers) will likely not work with spectre as they are not compatible with the official SDRPlay API**. 

## Supported Operating Systems and Platforms
This project is tested to be compatible with the following operating systems and architectures:

- Ubuntu 22.04.3 on (x86-64, arm64) architectures
- Debian GNU/Linux 12 (bookworm) on arm64 architecture

It may also work on other Linux distributions. Specifically, I have personally tested it on a Thinkpad P1G5 running Ubuntu 22.04.3 and a Raspberry Pi 4 Model B running Ubuntu Desktop, Raspberry Pi OS and Raspberry Pi OS Lite.

Support for Windows will be explored in the future.

## Installation

### **Prerequisites**
- Ensure the [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) is installed on your machine. This is required to build and run the container.
- Although the back-end is fully containerised, you must install any relevant third-party drivers on your host system.

---

### **Initial Setup**
1. Clone the repository into your preferred directory:  
   ```bash
   git clone https://github.com/jcfitzpatrick12/spectre.git
   ```

2. Navigate to the `spectre` directory:  
   ```bash
   cd spectre
   ```

3. Set the `SPECTRE_DATA_DIR_PATH` environment variable:  
   ```bash
   echo "export SPECTRE_DATA_DIR_PATH=$(pwd)/spectre-data" >> ~/.bashrc
   ```

4. Open a new terminal session to ensure the environment variable is updated.

---

### **Starting the `spectre-server`**
The `spectre-server` backend container must be running to respond to `spectre-cli` requests.

1. Build the Docker image using the `backend` directory:  
   ```bash
   docker build -t spectre-server ./backend
   ```

2. Run the `spectre-server` container:  
   ```bash
   chmod +x ./backend/run.sh && ./backend/run.sh
   ```

---

### **Running the `spectre-cli`**
1. Create a Python virtual environment:  
   ```bash
   python3 -m venv ./venv
   ```

2. Activate the virtual environment:  
   ```bash
   source ./venv/bin/activate
   ```

3. Install the required dependencies:  
   ```bash
   pip install -e .
   ```

4. Verify the CLI is operational:  
   ```bash
   spectre --version
   ```


## Contributing
This repository is in active development. If you are interested, feel free to contact  jcfitzpatrick12@gmail.com :)
