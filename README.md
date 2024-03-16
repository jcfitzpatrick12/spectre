# SPECTRE

## Overview
```SPECTRE``` is a program under development for the automated recording, analysis, and visualization of radio spectrograms. It consists of two primary components: ```spectre-host```, a CLI tool (with an accompanying ready-made, containerized environment) for recording radio spectrograms, and ```spectre-client```, a web-based application for viewing and analysis. This program builds upon the existing [```grso```](https://github.com/jcfitzpatrick12/grso) repository.

---

# spectre-host (in development)

## Introduction
```spectre-host```, the principal back-end component of the SPECTRE program, is a CLI tool for the automated recording of radio spectrograms. Underpinned with gnuradio, it aims to accommodate any SDR receiver with a gnuradio source block. Initial support is focused on the RSP* series via [```gr-sdrplay3```](https://github.com/fventuri/gr-sdrplay3). The tool is delivered with a ready-made, containerized environment.

## Supported Operating Systems
This project is tested to be compatible with the following operating systems:

- Ubuntu 22.04.3

It may also work on other Linux distributions and other Ubuntu versions. However, full compatibility is not guaranteed for operating systems other than the ones listed above.

## Features
...

## Installation
...

## Usage
1. Build the image from the Dockerfile:
```docker build -t spectre-host .```  
2. Run the container:
```bash run.sh```
3. Follow the in-terminal instructions.

## Contributing
...

## Improvements to Come
...


