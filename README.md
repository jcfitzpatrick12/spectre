# SPECTRE

## Overview
SPECTRE is a program under development for the automated recording, analysis, and visualization of radio spectrograms. It consists of two primary components: spectre-host, a CLI tool (with an accompanying ready-made, containerized environment) for recording radio spectrograms, and spectre-client, a web-based application for viewing and analysis. This program builds upon the existing [grso](https://github.com/jcfitzpatrick12/grso) repository.

---

# spectre-host (in development)

## Introduction
spectre-host, the principal back-end component of the SPECTRE program, is a CLI tool for the automated recording of radio spectrograms. Initial support is focused on the RSP* series via [gr-sdrplay3](https://github.com/fventuri/gr-sdrplay3). Leveraging gnuradio foundations, it aims to accommodate any SDR receiver with a gnuradio source block. The tool will be delivered with a ready-made, containerized environment, emphasizing ease of installation and minimal setup requirements.

## Supported Operating Systems

Currently being developed on Ubuntu 22.04.3, spectre-host may also function on other Linux distributions and Ubuntu versions. While striving for broad compatibility, optimal performance and full functionality are only assured for the specified operating system.

