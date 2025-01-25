# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# --------------------------------- # 
# Build the base stage
# --------------------------------- # 
FROM ubuntu:22.04 AS base

# Stop interactive dialogue (only for the duration of the build)
ARG DEBIAN_FRONTEND=noninteractive

# By default, use `tmp` as the working directory.
WORKDIR /tmp

# Update and upgrade the package index.
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y \
    gnuradio \
    libudev-dev \
    libusb-1.0-0 

# --------------------------------- # 
# Installing GNU Radio OOT modules
# --------------------------------- # 
FROM base AS gnuradio_oot_modules

# Install OOT module build dependencies.
RUN apt-get install -y \
    sudo \
    git \
    cmake \
    wget \
    expect

# Create /etc/udev directories manually, as they are not present in the base image.
RUN mkdir -p /etc/udev/rules.d /lib/udev/rules.d

# Install the SDRPlay API, and auto accept the licence agreement
COPY --chmod=0755 ./scripts/rsp_api.sh ./rsp_api.sh
RUN wget https://www.sdrplay.com/software/SDRplay_RSP_API-Linux-3.15.2.run && \
    chmod +x SDRplay_RSP_API-Linux-3.15.2.run && \
    ./rsp_api.sh

# Install all the OOT modules
COPY --chmod=0755 ./scripts/build_oot_module.sh build_oot_module.sh
RUN . ./build_oot_module.sh && \
    build_from_repo https://github.com/fventuri/gr-sdrplay3.git message-passing && \
    build_from_repo https://github.com/jcfitzpatrick12/gr-spectre.git v0.0.2


# --------------------------------- # 
# Install the spectre server
# --------------------------------- # 
FROM base AS spectre_server

# install dependencies required to install the rsp api in the image
RUN apt-get install -y \ 
    python3-pip

# Add the Python package source code
ADD src src

# Define the package requirements.
COPY ./pyproject.toml ./pyproject.toml

# Install the package and dependencies globally. 
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install .

# ------------------------------- # 
# Create the final runtime image
# ------------------------------- # 
FROM base AS final

# Define the spectre data directory path as an environment variable inside the container
ENV SPECTRE_DATA_DIR_PATH="/app/spectre/.spectre-data/"

# Copy in the sdrplay api service executable.
COPY --from=gnuradio_oot_modules /opt/sdrplay_api/sdrplay_apiService /opt/sdrplay_api/sdrplay_apiService

# Copy in the udev rules
COPY --from=gnuradio_oot_modules /etc/udev/rules.d /etc/udev/rules.d
COPY --from=gnuradio_oot_modules /lib/udev/rules.d /etc/lib/rules.d

# Copy in the OOT module files.
COPY --from=gnuradio_oot_modules /usr/local/lib /usr/local/lib
COPY --from=gnuradio_oot_modules /usr/local/include /usr/local/include
COPY --from=gnuradio_oot_modules /usr/include /usr/include
COPY --from=gnuradio_oot_modules /usr/lib /usr/lib

# Copy in the required files to start the spectre server
COPY --from=spectre_server /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages

# Set the final runtime working directory
WORKDIR /app

# Copy the script and set permissions in one step
COPY --chmod=0755 ./scripts/start.sh start.sh

# Default executable for the container
CMD ["/app/start.sh"]




