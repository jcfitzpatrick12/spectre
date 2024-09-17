# SPECTRE: Process, Explore and Capture Transient Radio Emissions

## Overview
`SPECTRE` is a program under development for the automated recording, analysis, and visualisation of radio spectrograms. It consists of three primary components: 
- `spectre` - a set of standalone Python modules for recording, analysing and visualising radio spectrograms 🐍
- `spectre-host` - a containerised environment for recording radio spectrograms powered by GNU Radio, which includes an accompanying CLI tool 📡 🐳
- `spectre-client` - a web-based application for viewing and analysis 💻 (planned for the future)
  
📢 **This project is under active development, with current efforts set on `spectre` and `spectre-host`. Once the testing framework is in place, we will be looking for contributors.**  📢 

---

# spectre-host

## Introduction
`spectre-host` is the principal back-end component of the SPECTRE program. It offers a containerised environment for the automated capture and analysis of radio spectrograms. Powered by GNU Radio, the framework is in place to accommodate any SDR receiver with a GNU Radio source block, simply. Initial support is focused on the SDRplay RSP* series via [`gr-sdrplay3`](https://github.com/fventuri/gr-sdrplay3). The container comes preinstalled with:

- **[`gnuradio`](https://github.com/gnuradio/gnuradio)**
- **[`gr-sdrplay3`](https://github.com/fventuri/gr-sdrplay3)**, which includes the SDRplay RSP* series GNU Radio source blocks.
- **[`gr-spectre`](https://github.com/jcfitzpatrick12/gr-spectre)**, which includes custom C++ GNU Radio sink blocks for streaming IQ data capture.
- The **`spectre`** CLI tool, for initiating data capture, creating configuration files and other utilities.
- **`cron`** and template scripts for daily data capture.

## Supported Receivers

Current supported receivers include:
- [RSP1A (from SDRPlay)](https://www.sdrplay.com/rsp1a/)
- [RSPduo (from SDRPlay)](https://www.sdrplay.com/rspduo/)

The framework is in place to integrate the following receivers, this is planned for the near future:
- RSP1, RSP1B, RSP2, RSPdx (via [`gr-sdrplay3`](https://github.com/fventuri/gr-sdrplay3))
- AirspyHF, BladeRF, HackRF, LimeSDR, PLUTO, RTLSDR (via [`Soapy`](https://wiki.gnuradio.org/index.php/Soapy))
- USRP SDRs

**Please note! SDRPlay clones (i.e. unofficially produced copies of SDRPlay receivers) will likely not work with SPECTRE as they are not compatible with the official SDRPlay API**. 

## Supported Operating Systems and Platforms
This project is tested to be compatible with the following operating systems and architectures:

- Ubuntu 22.04.3 on (x86-64, arm64) architectures
- Debian GNU/Linux 12 (bookworm) on arm64 architecture

It may also work on other Linux distributions. Specifically, I have personally tested it on a Thinkpad P1G5 running Ubuntu 22.04.3 and a Raspberry Pi 4 Model B running Ubuntu Desktop, Raspberry Pi OS and Raspberry Pi OS Lite.

Support for Windows will be explored in the future.

## Installation
We're still in active development, so this setup is not the final intended deployment method. In any case, feel free to dive in and tinker around with the current build. But be warned, everything might not be stable! Here's how you can get started:

**Prerequisites:**
Ensure you have [the docker engine](https://docs.docker.com/engine/install/ubuntu/) installed on your machine. This is essential for building and running the container.


**Install the RSP API on your host machine**  
First, download the RSP API from SDRPlay on your host machine by running (in your desired directory):  
```wget https://www.sdrplay.com/software/SDRplay_RSP_API-Linux-3.15.2.run```  
  
Alternatively, you can manually download it [directly from the SDRPlay website](https://www.sdrplay.com/api/).  
  
Run the API installation:  
```chmod +x ./SDRplay_RSP_API-Linux-3.15.2.run && ./SDRplay_RSP_API-Linux-3.15.2.run```  
  
With the installation successful, start the sdrplay API service:  
```sudo systemctl start sdrplay```

**Set up ```spectre```**  
Clone the repository (in your desired directory):  
```git clone https://github.com/jcfitzpatrick12/spectre.git```

Navigate to the ```spectre``` directory:   
```cd spectre```

Set the ```SPECTRE_DIR_PATH``` environment variable:  
```echo "export SPECTRE_DIR_PATH=$(pwd)" >> ~/.bashrc```  

**Set up ```spectre-host```**  
Please open a new shell and navigate to the ```host``` directory via:   
```cd $SPECTRE_DIR_PATH/host```

Build the Docker image:  
```sudo docker build -t spectre-host .```

Make the start script executable and run it:  
```chmod +x run.sh && ./run.sh```  

Now inside the container, check everything's up and running:  
```spectre -v ```

With the installation verified, you can freely use the suite of `spectre` CLI commands to create configuration files and capture data. You can exit the container using ```exit```


---

# spectre-client

## Introduction
While we are in development, we are creating a placeholder GUI which runs locally using [```tkinter```](https://docs.python.org/3/library/tkinter.html). This is being revised and improved following recent rework.

# Contributing
Once the testing framework is in place, we will be looking for contributors. In the meantime, feel free to contact jcfitzpatrick12@gmail.com if you are interested :)




