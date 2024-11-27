# SPECTRE: Process, Explore and Capture Transient Radio Emissions

## Overview

:loudspeaker: **This project is under active development**  :loudspeaker:

`spectre` is a program for recording and visualising radio spectrograms. Powered by [GNU Radio](https://www.gnuradio.org/), the framework is in place to accommodate any SDR receiver with a GNU Radio source block. 

**Features**:  

- Intuitive CLI tool :computer:
- Containerised backend :whale:
- Wide receiver support :satellite:
- Flexible, configurable data capture :gear:
- Live recording of radio spectrograms or IQ data :floppy_disk:
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
- USRP SDRs
- RTLSDR, AirspyHF, BladeRF, HackRF, LimeSDR, PLUTO (via [`Soapy`](https://wiki.gnuradio.org/index.php/Soapy))

**Please note! SDRPlay clones (i.e. unofficially produced copies of SDRPlay receivers) will likely not work with spectre as they are not compatible with the official SDRPlay API**. 

## Supported Operating Systems and Platforms
This project is tested to be compatible with the following operating systems and architectures:

- Ubuntu 22.04.3 on (x86-64, arm64) architectures
- Debian GNU/Linux 12 (bookworm) on arm64 architecture

It may also work on other Linux distributions. Specifically, I have personally tested it on a Thinkpad P1G5 running Ubuntu 22.04.3 and a Raspberry Pi 4 Model B running Ubuntu Desktop, Raspberry Pi OS and Raspberry Pi OS Lite.

Support for Windows will be explored in the future.

## Installation

**Prerequisites:**
Ensure you have [the docker engine](https://docs.docker.com/engine/install/ubuntu/) installed on your machine. This is essential for building and running the container.

...

## Contributing
This repository is in active development. If you are interested, feel free to contact  jcfitzpatrick12@gmail.com :)