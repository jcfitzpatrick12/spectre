# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# --------------------------------- # 
# Create the base stage
# --------------------------------- # 
FROM ubuntu:22.04 AS base

# Stop interactive dialogue, only for the duration of the build.
ARG DEBIAN_FRONTEND=noninteractive

# By default, use `tmp` as the working directory for each stage.
WORKDIR /tmp

# Update and upgrade the package index.
# Additionally, install dependencies which are both required for all
# the build stages, and will be present in the final runtime image.
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y \
    gnuradio libudev-dev libusb-1.0-0 wget 

# --------------------------------- # 
# Installing GNU Radio OOT modules
# --------------------------------- # 
FROM base AS gnuradio_oot_modules

# Install OOT module build dependencies.
RUN apt-get install -y \
    sudo git cmake expect 

# Create /etc/udev directories manually, as they are not present in the base image.
RUN mkdir -p /etc/udev/rules.d /lib/udev/rules.d

# Install the SDRPlay API, and auto accept the licence agreement
COPY --chmod=0755 ./scripts/expect/rsp_api.expect ./rsp_api.expect
RUN wget https://www.sdrplay.com/software/SDRplay_RSP_API-Linux-3.15.2.run && \
    chmod +x SDRplay_RSP_API-Linux-3.15.2.run && \
    expect rsp_api.expect

# Create an executable which can be used to detect sdrplay devices, as seen by the container
COPY ./scripts/cpp/sdrplay_find_devices.cpp sdrplay_find_devices.cpp
RUN g++ sdrplay_find_devices.cpp -o /usr/local/bin/sdrplay_find_devices -l sdrplay_api


# Install all the OOT modules.
COPY --chmod=0755 ./scripts/bash/build_oot_module.sh build_oot_module.sh
RUN . ./build_oot_module.sh && \
    build_from_repo https://github.com/fventuri/gr-sdrplay3.git message-passing && \
    build_from_repo https://github.com/jcfitzpatrick12/gr-spectre.git v0.0.2


# --------------------------------- # 
# Install the flask server
# --------------------------------- # 
FROM base AS flask_server

# Copy in the flask server source code.
ADD src src

# Copy in the build requirements.
COPY ./pyproject.toml ./pyproject.toml

# Install the dependencies system-wide.
RUN apt-get install -y \
    python3-pip && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install .

# ------------------------------- # 
# Create the final runtime stage
# ------------------------------- # 
FROM base AS runtime

# Set the working directory for the final runtime image.
WORKDIR /app

# Define the spectre data directory path as an environment variable inside the container
ENV SPECTRE_DATA_DIR_PATH="/app/.spectre-data"

# Install the USRP Hardware driver
RUN apt-get install -y \
    uhd-host && \
    /usr/lib/uhd/utils/uhd_images_downloader.py

# Copy in the udev rules
COPY --from=gnuradio_oot_modules /etc/udev/rules.d /etc/udev/rules.d
COPY --from=gnuradio_oot_modules /lib/udev/rules.d /lib/udev/rules.d

# Copy in the OOT module files.
COPY --from=gnuradio_oot_modules /usr/local/lib /usr/local/lib
COPY --from=gnuradio_oot_modules /usr/local/include /usr/local/include
COPY --from=gnuradio_oot_modules /usr/include /usr/include
COPY --from=gnuradio_oot_modules /usr/lib /usr/lib

# Copy in the sdrplay executables
COPY --from=gnuradio_oot_modules /opt/sdrplay_api/sdrplay_apiService /opt/sdrplay_api/sdrplay_apiService
COPY --from=gnuradio_oot_modules /usr/local/bin/sdrplay_find_devices /usr/local/bin/sdrplay_find_devices

# Copy in system-wide python packages for the flask server.
COPY --from=flask_server /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages

# Copy in the start script, and set it as the default executable for the container
COPY --chmod=0755 ./scripts/bash/start.sh ./start.sh
CMD ["./start.sh"]


# ------------------------------- # 
# Create the development stage
# ------------------------------- # 
FROM runtime AS development

# Set environment variables required to enable gui functionality.
ENV DISPLAY=:0
ENV XDG_RUNTIME_DIR=/tmp/runtime-root
ENV NO_AT_BRIDGE=1

RUN apt-get install -y \
    # Install development tools.
    git python3-pip vim \
    # Required for the gnuradio GUI to run inside the container
    libgtk-3-dev x11-apps \
    # Subdue some warnings flagged on starting gnuradio-companion
    libcanberra-gtk-module libcanberra-gtk3-module \
    # Subdue a warning when "opening from file" in gnuradio
    dbus-x11 && \
    # Upgrade packages for building and distributing `spectre-core`.
    pip install --upgrade build twine

# Clone then install the latest `spectre` and `spectre-core` code, ready for development.
COPY --chmod=0755 ./scripts/bash/install_spectre_latest.sh ./install_spectre_latest.sh 
RUN ./install_spectre_latest.sh && rm ./install_spectre_latest.sh

# Copy in the OOT module grc files
COPY --from=gnuradio_oot_modules /usr/local/share/gnuradio/grc/blocks /usr/local/share/gnuradio/grc/blocks

CMD ["/bin/bash"]