<h1 align="center">
  SPECTRE: Process, Explore and Capture Transient Radio Emissions
</h1>

<div align="center">
  <img src="docs/gallery/solar_radio.png" width="30%" hspace="10" alt="Solar Radio Observations">
  <img src="docs/gallery/spectre.png" width="30%" hspace="10" alt="SPECTRE Logo">
  <img src="docs/gallery/fm_radio.png" width="30%" hspace="10" alt="FM Band">
</div>


## Overview

📢 **This project is under active development. Contributors welcome!** 📢

`spectre` is a receiver-agnostic program for recording and visualising radio spectrograms. Powered by [GNU Radio](https://www.gnuradio.org/).


### **Features**
- 💻 Intuitive CLI tool  
- 🐳 Simple installation with Docker
- 🛰️ Wide receiver support  
- 💾 Live recording of radio spectrograms and I/Q data  
- ⚙️ Flexible, configurable data capture   
- 🔧 Developer-friendly and extensible

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

### **Starting Spectre**

1. **Clone the repository**  
   Clone the \`spectre\` GitHub repository and navigate to its root directory:  
   ```bash
   git clone https://github.com/jcfitzpatrick12/spectre.git && cd spectre
   ```

2. **Start the containers**  
   Ensure any connected receivers are plugged in, then create and run the containers:  
   ```bash
   docker compose up --build
   ```

3. **Set up an alias for the CLI**  
   In a new terminal tab, set up an alias for \`spectre\` on your host machine:  
   ```bash
   echo "alias spectre='docker exec spectre-cli spectre'" >> ~/.bashrc && . ~/.bashrc
   ```
   This allows you to run \`spectre\` directly from the host.


### **Checking your receiver is detected**  
If you have a physical receiver connected, it's a good idea to verify that the `spectre-server` can detect it.

- For SDRplay receivers, run:  
   ```bash
   docker exec spectre-server sdrplay_find_devices
   ```

- For USRP receivers, run:  
   ```bash
   docker exec spectre-server uhd_find_devices
   ```

If this is the first time you're running the container since plugging in the device, it may not be detected. Ensure the receiver is still connected, then try restarting the containers again.


## **Quick Start for Developers**
1. **Start the containers**  
   Ensure any connected receivers are plugged in before running the containers, pointing to the development compose file:  
   ```bash
   docker compose -f docker-compose.dev.yml up --build
   ```

You can then use [dev-containers](https://code.visualstudio.com/docs/devcontainers/containers) to work on the latest versions of `spectre-core` and `spectre`.

## Contributing
This repository is in active development. If you are interested, feel free to contact  jcfitzpatrick12@gmail.com :)
