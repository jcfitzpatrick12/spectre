# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# --------------------------------- # 
# Build the base stage
# --------------------------------- # 
# Use an Ubuntu image (exact version of 22.04)
FROM ubuntu@sha256:3d1556a8a18cf5307b121e0a98e93f1ddf1f3f8e092f1fddfd941254785b95d7 AS base

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
    gnuradio=3.10.1.1-2 \
    libudev-dev=249.11-0ubuntu3.12 \
    libusb-1.0-0=2:1.0.25-1ubuntu2

# --------------------------------- # 
# Installing GNU Radio OOT modules
# --------------------------------- # 
FROM base AS gnuradio_oot_modules

# Install OOT module build dependencies.
RUN apt-get install -y \
    sudo=1.9.9-1ubuntu2.4 \
    git=1:2.34.1-1ubuntu1.12 \
    cmake=3.22.1-1ubuntu1.22.04.2 \
    wget=1.21.2-2ubuntu1.1 \
    expect=5.45.4-2build1

# Create /etc/udev directories manually, as they are not present in the base image.
RUN mkdir -p /etc/udev/rules.d /lib/udev/rules.d

# Install the SDRPlay API, and auto accept the licence agreement
COPY --chmod=0755 ./scripts/rsp_api.sh ./rsp_api.sh
RUN wget https://www.sdrplay.com/software/SDRplay_RSP_API-Linux-3.15.2.run && \
    chmod +x SDRplay_RSP_API-Linux-3.15.2.run && \
    ./rsp_api.sh

# Install all the OOT modules.
COPY --chmod=0755 ./scripts/build_oot_module.sh build_oot_module.sh
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
    python3-pip=22.0.2+dfsg-1ubuntu0.5 && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install .

# ------------------------------- # 
# Create the final runtime stage
# ------------------------------- # 
FROM base AS runtime

# Set the working directory for the final runtime image.
WORKDIR /app

# Define the spectre data directory path as an environment variable inside the container
ENV SPECTRE_DATA_DIR_PATH="/app/.spectre-data/"

# Copy in the udev rules
COPY --from=gnuradio_oot_modules /etc/udev/rules.d /etc/udev/rules.d
COPY --from=gnuradio_oot_modules /lib/udev/rules.d /etc/lib/rules.d

# Copy in the OOT module files.
COPY --from=gnuradio_oot_modules /usr/local/lib /usr/local/lib
COPY --from=gnuradio_oot_modules /usr/local/include /usr/local/include
COPY --from=gnuradio_oot_modules /usr/include /usr/include
COPY --from=gnuradio_oot_modules /usr/lib /usr/lib

# Copy in the sdrplay api service executable.
COPY --from=gnuradio_oot_modules /opt/sdrplay_api/sdrplay_apiService /opt/sdrplay_api/sdrplay_apiService

# Copy in system-wide python packages for the flask server.
COPY --from=flask_server /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages

# Copy the script and set permissions in one step
COPY --chmod=0755 ./scripts/start.sh ./start.sh

# Default executable for the container
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
    # Install python3 and git, required for development.
    git=1:2.34.1-1ubuntu1.12 \
    python3-pip=22.0.2+dfsg-1ubuntu0.5 \
    # lbgtk-3-dev and x11-apps are required for the gnuradio GUI to run inside the container
    libgtk-3-dev=3.24.33-1ubuntu2.2 \
    x11-apps=7.7+8build2 \
    # libcanberra packages are installed to subdue some warnings flagged on starting gnuradio-companion
    libcanberra-gtk-module=0.30-10ubuntu1.22.04.1 \
    libcanberra-gtk3-module=0.30-10ubuntu1.22.04.1 \
    # dbus x11 stops a warning when "opening from file" in gnuradio
    dbus-x11=1.12.20-2ubuntu4.1 && \
    # Upgrade packages for building and distributing `spectre-core`.
    pip install --upgrade \
    build twine

# Clone then install the latest `spectre` and `spectre-core` code, ready for development.
COPY --chmod=0755 ./scripts/install_spectre_latest.sh ./install_spectre_latest.sh 
RUN ./install_spectre_latest.sh && rm ./install_spectre_latest.sh

CMD ["/bin/bash"]



