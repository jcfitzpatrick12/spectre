<h1 align="center">
  SPECTRE: Process, Explore and Capture Transient Radio Emissions
</h1>

<div align="center">
  <img src="docs/gallery/solar_radio.png" width="30%" hspace="10" alt="Solar Radio Observations">
  <img src="docs/gallery/spectre.png" width="30%" hspace="10" alt="SPECTRE Logo">
  <img src="docs/gallery/fm_radio.png" width="30%" hspace="10" alt="FM Band">
</div>


## Overview

📢 **This project is under active development, expect breaking changes. Contributors welcome!** 📢

`spectre` is a receiver-agnostic program for recording and visualising radio spectrograms. Powered by [GNU Radio](https://www.gnuradio.org/).


### **Features**
- 💻 Intuitive CLI tool
- 🐳 Simple installation with Docker
- 🛰️ Wide receiver support  
- 💾 Live recording of radio spectrograms and I/Q data  
- ⚙️ Flexible, configurable data capture
- ✏️ Services exposed with a discoverable RESTful API
- 🔧 Developer-friendly and extensible


### **Demo**
Capture data from SDRs, simply.

1. **Create a configuration file**  
   Write a new configuration file to collect data from the SDRPlay RSP1A at a fixed center frequency:  
   ```bash
   spectre create capture-config --receiver rsp1a --mode fixed_center_frequency --tag rsp1a-example
   ```
   
2. **Capture data**  
   Start streaming I/Q samples from the receiver, and automatically post process the data into radio spectrograms:  
   ```bash
   spectre start session --tag rsp1a-example --seconds 30
   ```
   
## Supported Receivers

Our abstract framework can support any receiver with a source block in GNU Radio. If you have a receiver that isn't supported, reach out, and we can look into adding support for it!

### **Currently Supported Receivers**
- [RSP1A (from SDRPlay)](https://www.sdrplay.com/rsp1a/)  
- [RSPduo (from SDRPlay)](https://www.sdrplay.com/rspduo/)  
- [USRP B200mini (from Ettus Research)](https://www.ettus.com/all-products/usrp-b200mini/)

### **Planned Future Support**
- RSP1, RSP1B, RSP2, RSPdx 
- Any USRP SDR 
- RTLSDR, AirspyHF, BladeRF, HackRF, LimeSDR, PLUTO (via [`Soapy`](https://wiki.gnuradio.org/index.php/Soapy))  

**⚠️ Note:**  
SDRPlay clones (i.e., unofficially produced copies of SDRPlay receivers) will likely not work with spectre as they are not compatible with the official SDRPlay API.  
## Supported Platforms
`spectre` is expected to be compatible with most Linux distributions.

The following operating systems and architectures have been verified:   
- **ThinkPad P1G5** running:
  - Ubuntu 22.04.3  
- **Raspberry Pi 4 Model B** running:
  - Ubuntu Desktop  
  - Raspberry Pi OS  
  - Raspberry Pi OS Lite  

macOS compatibility will be explored in the future.

## Quick Start

### **Prerequisites**
To get going, you'll need the following installed on your machine:  
| Prerequisite      | How to Install | Do I Already Have It? |
|------------------|---------------|-----------------------|
| **Docker Engine** | [Install Docker Engine](https://docs.docker.com/engine/install/) | Run `docker --version` |
| **Git**          | [Getting Started - Installing Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) | Run `git --version` |

### **Getting started**

1. **Clone the repository**  
   Clone the `spectre` GitHub repository and navigate to its root directory:  
   ```bash
   git clone https://github.com/jcfitzpatrick12/spectre.git && cd spectre
   ```

2. **Start the containers**  
   Ensure any receivers are connected, then create and run the containers:  
   ```bash
   docker compose up --build
   ```

3. **Create an alias for the CLI**  
   In a new terminal tab, set up the following alias:    
   ```bash
   echo "alias spectre='docker exec spectre-cli spectre'" >> ~/.bashrc && . ~/.bashrc
   ```
   This lets you run `spectre-cli` commands as if they were executed directly on the host.

4. **Good to go!**  
   Verify everything is up and running with:    
   ```bash
   spectre --help
   ```
   
### **Check your receiver is detected**  
If you have a physical receiver connected, it's a good idea to verify that the `spectre-server` can detect it.

- For SDRplay receivers, run:  
   ```bash
   docker exec spectre-server sdrplay_find_devices
   ```

- For USRP receivers, run:  
   ```bash
   docker exec spectre-server uhd_find_devices
   ```

If this is the first time you're running the containers since plugging in the device, it may not be detected. Ensure the receiver is still connected, then restart the `spectre-server` with:  
   ```bash
   docker compose restart spectre-server
   ```

### **Run the CLI without Docker**
You can also run the CLI locally, without the `spectre-cli` container.

1. **Create and activate a Python virtual environment**
   Create and activate a Python virtual environment dedicated for the `spectre-cli`:  
   ```bash
   python3 -m venv ./.venv && . ./.venv/bin/activate
   ```
2. **Install the dependencies**  
   Install the dependencies into the newly activated virtual environment.:  
   ```bash
   pip install ./cli
   ```
3. **Good to go!**  
   Verify everything is up and running with:      
   ```bash
   spectre --help
   ```

## **Quick Start for Developers**
For development, use the development Compose file:    
   ```bash
   docker compose --file docker-compose.dev.yml up --build
   ```

[spectre](https://github.com/jcfitzpatrick12/spectre) is the primary application repository, with server-side implementations available in a separate Python package called [spectre-core](https://github.com/jcfitzpatrick12/spectre-core). Once the containers are running, you can use [dev-containers](https://code.visualstudio.com/docs/devcontainers/containers) to work on the latest versions of `spectre-core` and `spectre`.

**⚠️ Note:**  
If you're working with SDRPlay receivers, you will have to start the SDRPlay API manually.

## Contributing
This repository is in active development. If you are interested, feel free to contact  jcfitzpatrick12@gmail.com :)
