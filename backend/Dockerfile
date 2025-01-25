# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# --------------------------------- # 
# Build the base stage
# --------------------------------- # 
FROM ubuntu:22.04 AS base

# Stop interactive dialogue (only for the duration of the build)
ARG DEBIAN_FRONTEND=noninteractive

# By default, set `tmp` as the working directory for the `base` stage.
WORKDIR /tmp

# Update and upgrade the package index for the `base` stage
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y \
    gnuradio \
    libudev-dev \
    libusb-1.0-0 

# --------------------------------- # 
# Installing GNU Radio OOT modules
# --------------------------------- # 
FROM base AS gnuradio_oot_module

# Install build dependencies
RUN apt-get install -y \
    sudo \
    git \
    cmake 

# Create /etc/udev directories manually, as they are missing in the base image.
RUN mkdir -p /etc/udev/rules.d /lib/udev/rules.d

# Copy in the file fix script, wich resolves a cmake OOT module error.
COPY ./scripts/install/build_oot_module.sh build_oot_module.sh
RUN chmod +x build_oot_module.sh 

# --------------------------------- # 
# Install gr-sdrplay3
# --------------------------------- # 
FROM gnuradio_oot_module AS gr_sdrplay

# copy in the script which auto-accepts the licence agreement
COPY ./scripts/install/rsp_api.sh ./rsp_api.sh

# install dependencies required to install the rsp api in the image
RUN apt-get install -y \ 
    wget \
    expect 

# Install the SDRPlay API, auto accepting the licence agreement
RUN wget https://www.sdrplay.com/software/SDRplay_RSP_API-Linux-3.15.2.run && \
    chmod +x ./SDRplay_RSP_API-Linux-3.15.2.run && \
    chmod +x ./rsp_api.sh && \
    ./rsp_api.sh


# Install the OOT module
RUN . ./build_oot_module.sh && \
    build_from_repo https://github.com/fventuri/gr-sdrplay3.git message-passing

# --------------------------------- # 
# Install gr-spectre
# --------------------------------- # 
FROM gnuradio_oot_module AS gr_spectre

# Install the OOT module
RUN . ./build_oot_module.sh && \
    build_from_repo https://github.com/jcfitzpatrick12/gr-spectre.git v0.0.2


# --------------------------------- # 
# Install the spectre server
# --------------------------------- # 
FROM base AS spectre_server

# install dependencies required to install the rsp api in the image
RUN apt-get install -y \ 
    python3-pip \
    python3.10-venv

# Add the Python package source code
ADD src src

# Define the package requirements.
COPY ./pyproject.toml ./pyproject.toml

# Install the package and dependencies globally. 
RUN python3 -m venv ./.venv && \
    ./.venv/bin/pip install --upgrade pip && \
    ./.venv/bin/pip install .

# ------------------------------- # 
# Create the final runtime image
# ------------------------------- # 
FROM base AS final

# Define the spectre data directory path as an environment variable inside the container
ENV SPECTRE_DATA_DIR_PATH="/home/spectre/.spectre-data/"

# gr-sdrplay3
# Copy in the sdrplay api service executable. This will be manually run without systemctl.
COPY --from=gr_sdrplay /opt/sdrplay_api/sdrplay_apiService /opt/sdrplay_api/sdrplay_apiService
# Copy in the udev rules for SDRPlay devices
COPY --from=gr_sdrplay /etc/udev/rules.d /etc/udev/rules.d
COPY --from=gr_sdrplay /lib/udev/rules.d /etc/lib/rules.d
# Copy in the OOT module files.
COPY --from=gr_sdrplay /usr/local/lib /usr/local/lib
COPY --from=gr_sdrplay /usr/local/include /usr/local/include
COPY --from=gr_sdrplay /usr/local/share/gnuradio/grc/blocks/ /usr/local/share/gnuradio/grc/blocks/
COPY --from=gr_sdrplay /usr/include /usr/include
COPY --from=gr_sdrplay /usr/lib /usr/lib


# gr-spectre
# Copy in the OOT module files.
COPY --from=gr_spectre /usr/local/lib /usr/local/lib
COPY --from=gr_spectre /usr/local/include /usr/local/include
COPY --from=gr_spectre /usr/local/share/gnuradio/grc/blocks/ /usr/local/share/gnuradio/grc/blocks/
COPY --from=gr_spectre /usr/include /usr/include
COPY --from=gr_spectre /usr/lib /usr/lib


# # Copy in the required spectre-server Python files
COPY --from=spectre_server /tmp/.venv/lib/python3.10/site-packages /usr/local/lib/python3.1/dist-packages

CMD ["python3.11", "-m", "spectre_server"]




