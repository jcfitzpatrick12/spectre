# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# --------------------------------- # 
# Create the base stage.
# --------------------------------- # 
FROM ubuntu:22.04 AS base

# Stop interactive dialogue, only for the duration of the build.
ARG DEBIAN_FRONTEND=noninteractive

# By default, we use the /tmp directory to hold build artifacts.
WORKDIR /tmp

# Explictly set the user to root by default for each stage.
USER root

# Install dependencies which are both required for all the build stages, and will be present in the final runtime image.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnuradio \
    libudev-dev \
    libusb-1.0-0 \
    wget \
    gosu \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# --------------------------------- # 
# Install shared build dependencies.
# --------------------------------- # 
FROM base AS cpp_build

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    cmake \
    make \
    libboost-all-dev \
    gnuradio-dev && \
    rm -rf /var/lib/apt/lists/*

# --------------------------------- #
# Install SDRPlay API.
# --------------------------------- #
FROM base AS sdrplay_api

WORKDIR /tmp/sdrplay_api

ARG SDRPLAY_API_MAJ_MIN=3.15
ARG SDRPLAY_API_PATCH=2
ARG SDRPLAY_VERSION=${SDRPLAY_API_MAJ_MIN}.${SDRPLAY_API_PATCH}
ARG SDRPLAY_API_LIB=libsdrplay_api

# Install the SDRplay API.
RUN mkdir -p /opt/sdrplay_api/include \
             /opt/sdrplay_api/lib \
             /opt/sdrplay_api/bin \
             /opt/sdrplay_api/share/doc/ && \
    wget https://www.sdrplay.com/software/SDRplay_RSP_API-Linux-${SDRPLAY_VERSION}.run && \
    sh SDRplay_RSP_API-Linux-${SDRPLAY_VERSION}.run --tar xf && \
    ARCH=$(uname -m | sed 's/aarch64/arm64/' | sed 's/x86_64/amd64/') && \
    cp ${ARCH}/${SDRPLAY_API_LIB}.so.${SDRPLAY_API_MAJ_MIN} /opt/sdrplay_api/lib/ && \
    cp ${ARCH}/sdrplay_apiService /opt/sdrplay_api/bin/ && \
    cp inc/* /opt/sdrplay_api/include/ && \
    cp sdrplay_license.txt /opt/sdrplay_api/share/doc/ && \
    ln --symbolic ${SDRPLAY_API_LIB}.so.${SDRPLAY_API_MAJ_MIN} /opt/sdrplay_api/lib/${SDRPLAY_API_LIB}.so.3 && \
    ln --symbolic ${SDRPLAY_API_LIB}.so.${SDRPLAY_API_MAJ_MIN} /opt/sdrplay_api/lib/${SDRPLAY_API_LIB}.so

# --------------------------------------------- #
# Create an executable to find SDRplay devices.
# --------------------------------------------- #
FROM cpp_build AS sdrplay_find_devices

WORKDIR /tmp/sdrplay_find_devices

COPY --from=sdrplay_api /opt/sdrplay_api/include/ /usr/include/
COPY --from=sdrplay_api /opt/sdrplay_api/lib/ /usr/lib/
COPY ./scripts/cpp/sdrplay_find_devices.cpp sdrplay_find_devices.cpp

RUN mkdir -p /opt/sdrplay_find_devices/bin && \
    g++ sdrplay_find_devices.cpp -l sdrplay_api -o /opt/sdrplay_find_devices/bin/sdrplay_find_devices


# --------------------------------------------- #
# Install UHD dependencies.
# --------------------------------------------- #
FROM cpp_build AS uhd

WORKDIR /tmp/uhd

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-requests \
    python3-setuptools \
    libusb-1.0-0-dev && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 -b v4.8.0.0 https://github.com/EttusResearch/uhd.git && \
    cd uhd/host && \
    mkdir build && \
    cd build  && \
    cmake -Wno-dev \
          -DCMAKE_INSTALL_PREFIX=/opt/uhd \
          -DENABLE_B200=ON \
          -DENABLE_USB=ON \
          -DENABLE_LIBUHD=ON \
          -DENABLE_PYTHON_API=ON \
          -DENABLE_UTILS=ON \
          -DINSTALL_UDEV_RULES=ON \
          -DENABLE_EXAMPLES=OFF \
          -DENABLE_TESTS=OFF \
          -DENABLE_MAN_PAGES=OFF \
          -DENABLE_DOXYGEN=OFF \
          -DENABLE_MANUAL=OFF \
          -DENABLE_C_API=OFF \
          -DENABLE_E320=OFF \
          -DENABLE_E300=OFF \
          -DENABLE_N230=OFF \
          -DENABLE_OCTOCLOCK=OFF \
          -DENABLE_B100=OFF \
          -DENABLE_USRP1=OFF \
          -DENABLE_RFNOC=OFF \
          -DENABLE_FPGA_MANAGER=OFF \
          -DENABLE_BLADE=OFF \
          -DENABLE_MPM=OFF \
    .. && \
    make && \
    make install

RUN /opt/uhd/lib/uhd/utils/uhd_images_downloader.py --install-location=/opt/uhd/share/uhd/images/ \
                                                    --types b2xx

# --------------------------------------------- #
# Install the gr-sdrplay3 OOT module.
# --------------------------------------------- #
FROM cpp_build AS gr_sdrplay3

WORKDIR /tmp

COPY --from=sdrplay_api /opt/sdrplay_api/include/ /usr/include/
COPY --from=sdrplay_api /opt/sdrplay_api/lib/ /usr/lib/

COPY --chmod=0755 ./scripts/bash/build_oot_module.sh build_oot_module.sh
RUN . ./build_oot_module.sh && \
    build_from_repo https://github.com/jcfitzpatrick12/gr-sdrplay3.git message-passing 

# --------------------------------------------- #
# Install the gr-spectre OOT module.
# --------------------------------------------- #
FROM cpp_build AS gr_spectre

WORKDIR /tmp

COPY --chmod=0755 ./scripts/bash/build_oot_module.sh build_oot_module.sh
RUN . ./build_oot_module.sh && \
    build_from_repo https://github.com/jcfitzpatrick12/gr-spectre.git v0.0.2

# --------------------------------- # 
# Install the spectre server.
# --------------------------------- # 
FROM base AS spectre_server

# Set up a working directory for the Python build
WORKDIR /tmp/spectre_server

# Install Python build dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip && \
    python3 -m pip install --upgrade pip && \
    rm -rf /var/lib/apt/lists/*

# Copy in the source code and build requirements.
COPY pyproject.toml ./
COPY src src

# Finally, install the Python dependencies into the virtual environment.
RUN python3 -m pip install --upgrade pip && \
    pip install .

COPY gunicorn.conf.py /opt/spectre_server/

# --------------------------------- # 
# Create the final runtime stage.
# --------------------------------- # 
FROM base AS runtime

LABEL maintainer="Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>" \
      version="0.0.8" \
      description="Docker image for running the `spectre-server`." \
      license="GPL-3.0-or-later"

WORKDIR /app

ENV SPECTRE_DATA_DIR_PATH="/app/.spectre-data"
ENV MPLCONFIGDIR="/app/.mplconfigdir"
ENV UHD_IMAGES_DIR="/usr/share/uhd/images"

# Copy in the SDRplay runtime dependencies.
COPY --from=sdrplay_api /opt/sdrplay_api/bin /usr/bin
COPY --from=sdrplay_api /opt/sdrplay_api/include /usr/include
COPY --from=sdrplay_api /opt/sdrplay_api/lib /usr/lib
COPY --from=sdrplay_api /opt/sdrplay_api/share /usr/share
COPY --from=sdrplay_find_devices /opt/sdrplay_find_devices/bin /usr/bin

# Copy in the UHD runtime dependencies.
COPY --from=uhd /opt/uhd/include /usr/include
COPY --from=uhd /opt/uhd/lib /usr/lib
COPY --from=uhd /opt/uhd/bin /usr/bin
COPY --from=uhd /opt/uhd/share /usr/share
COPY --from=uhd /opt/uhd/lib/uhd/utils/uhd-usrp.rules /etc/udev/rules.d/

# Copy in the gr-sdrplay3 OOT module runtime dependencies.
COPY --from=gr_sdrplay3 /opt/gr_sdrplay3/include/ /usr/include/
COPY --from=gr_sdrplay3 /opt/gr_sdrplay3/lib/ /usr/lib
COPY --from=gr_sdrplay3 /opt/gr_sdrplay3/local/ /usr/local/
COPY --from=gr_sdrplay3 /opt/gr_sdrplay3/share/ /usr/share/

# Copy in the gr-spectre OOT module runtime dependencies.
COPY --from=gr_spectre /opt/gr_spectre/include/ /usr/include/
COPY --from=gr_spectre /opt/gr_spectre/lib/ /usr/lib
COPY --from=gr_spectre /opt/gr_spectre/local/ /usr/local/
COPY --from=gr_spectre /opt/gr_spectre/share/ /usr/share/

# Copy in the spectre server runtime dependencies.
COPY --from=spectre_server /usr/local/lib/python3.10/dist-packages/ /usr/local/lib/python3.10/dist-packages/
COPY --from=spectre_server /opt/spectre_server/gunicorn.conf.py /app/gunicorn.conf.py

# Copy in the scripts which will run when the container starts.
COPY --chmod=0755 scripts/bash/entrypoint.sh entrypoint.sh
COPY --chmod=0755 scripts/bash/cmd.sh cmd.sh

# Add a non-root user to run the application.
RUN useradd -u 1000 -M -d /app appuser

# We cannot use the `USER` directive, since non-root user running the application can't write to the mounted volume.
# So, the container starts as root to change ownership of the /app directory,  then drops privileges and runs as the 
# non-root user to execute the application.
# See https://stackoverflow.com/questions/65574334/docker-is-it-safe-to-switch-to-non-root-user-in-entrypoint for 
# some discussion on this approach.
ENTRYPOINT ["/bin/sh", "entrypoint.sh"]
CMD ["/app/cmd.sh"]


# ----------------------------------------------------------- # 
# Optional target, where you can run the application as root.
# ----------------------------------------------------------- # 
FROM runtime AS root_runtime

# Return to the default entrypoint and run the application as root.
ENTRYPOINT [ ]
CMD ["/app/cmd.sh"]


# --------------------------------- # 
# Create the development stage.
# --------------------------------- # 
FROM runtime AS development

# Install development tools.
RUN apt-get update && apt-get install -y \
    git \
    python3-venv \
    python3-setuptools \
    python3-pip \
    python3-wheel \
    twine \
    vim 

# Clone the `spectre` repository and install the server in editable mode
RUN git clone https://github.com/jcfitzpatrick12/spectre.git --no-checkout && cd spectre && \
    git sparse-checkout init --no-cone && \
    git sparse-checkout set backend/ && \
    git checkout && \
    pip install -e backend/

# Get the latest version of `spectre-core` and install it in editable mode
RUN git clone https://github.com/jcfitzpatrick12/spectre-core.git && cd spectre-core && \
    git checkout main && \
    pip install -e .

# Get the latest version of `gr-spectre` and install it in editable mode.
# Developers can rebuild again, if required.
RUN git clone https://github.com/jcfitzpatrick12/gr-spectre.git && cd gr-spectre && \
    git checkout main
    
# Disable the existing entrypoint and start up commands, and run as root.
ENTRYPOINT [ ]
CMD [ ]

