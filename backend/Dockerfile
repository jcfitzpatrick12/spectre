# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
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

# Install dependencies which are both required for all the build stages, and must be present in the final runtime image.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gosu \
    python3 \
    wget \
    ca-certificates \
    libpython3.10 \
    libusb-1.0-0 \
    liblog4cpp5-dev \
    libspdlog1 \
    libuhd4.1.0 \
    libboost-program-options1.74.0 \
    libboost-thread1.74.0 \
    libboost-chrono1.74.0 \
    libboost-filesystem1.74.0 \
    libboost-system1.74.0 \
    libsoapysdr0.8 \
    soapysdr-tools \
    libfftw3-3 && \
    rm -rf /var/lib/apt/lists/*

# -------------------------------------- # 
# Install shared build dependencies.
# -------------------------------------- # 
FROM base AS build

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    cmake \
    build-essential \
    gnuradio-dev \
    libusb-1.0-0-dev \
    libsoapysdr-dev \
    libspdlog-dev \
    libudev-dev \
    pybind11-dev \
    python3-packaging \
    python3-pip \
    python3-setuptools \
    python3-requests \
    python3-mako \
    python3-numpy \
    python3-build \
    python3-yaml && \
    python3 -m pip install --upgrade pip setuptools build && \
    rm -rf /var/lib/apt/lists/*

# --------------------------------------------- #
# Install UHD.
# --------------------------------------------- #
FROM build AS uhd

WORKDIR /tmp

# Minimal UHD install, to reduce image size.
RUN git clone --branch v4.1.0.0  --depth 1 https://github.com/EttusResearch/uhd.git && \
    cd uhd/host && \
    mkdir build && \
    cd build && \
    cmake -Wno-dev \
    -DCMAKE_INSTALL_PREFIX=/opt/uhd \
    -DENABLE_B200=ON \
    -DENABLE_LIBUHD=ON \
    -DENABLE_USB=ON \
    -DENABLE_PYTHON_API=ON \
    -DENABLE_UTILS=ON \
    -DENABLE_EXAMPLES=OFF \
    -DENABLE_TESTS=OFF \
    -DENABLE_MAN_PAGES=OFF \
    -DENABLE_DOXYGEN=OFF \
    -DENABLE_MANUAL=OFF \
    -DENABLE_C_API=OFF \
    -DENABLE_USRP2=OFF \
    -DENABLE_X300=OFF \
    -DENABLE_X400=OFF \
    -DENABLE_N300=OFF \
    -DENABLE_N320=OFF \
    -DENABLE_SIM=OFF \
    -DENABLE_MPMD=OFF \
    -DENABLE_B100=OFF \
    -DENABLE_USRP1=OFF \
    -DENABLE_OCTOCLOCK=OFF \
    .. && \
    make -j"$(nproc)" && \
    make install && \
    rm -rf /tmp/*

RUN /opt/uhd/lib/uhd/utils/uhd_images_downloader.py --install-location=/opt/uhd/share/uhd/images/ \
                                                    --types b2xx && \
    rm -rf /tmp/*

# --------------------------------------------- #
# Install Volk.
# --------------------------------------------- #
FROM build AS volk

WORKDIR /tmp

COPY --from=uhd /opt/uhd/include /usr/include
COPY --from=uhd /opt/uhd/lib /usr/lib
COPY --from=uhd /opt/uhd/bin /usr/bin
COPY --from=uhd /opt/uhd/share /usr/share

# Minimal volk install, to reduce image size.
RUN git clone --branch v2.5.1 --recursive --depth 1 --shallow-submodules https://github.com/gnuradio/volk.git && \
    cd volk && \
    mkdir build && \
    cd build && \
    cmake -Wno-dev \
    -DCMAKE_INSTALL_PREFIX=/opt/volk \
    -DCMAKE_BUILD_TYPE=MinSizeRel \
    -DBUILD_TESTING=OFF \
    -DENABLE_TESTING=OFF \
    .. && \
    make -j"$(nproc)" && \
    make install && \
    rm -rf /tmp/*


# --------------------------------------------- #
# Install GNU Radio.
# --------------------------------------------- #
FROM build AS gnuradio

WORKDIR /tmp

COPY --from=uhd /opt/uhd/include /usr/include
COPY --from=uhd /opt/uhd/lib /usr/lib
COPY --from=uhd /opt/uhd/bin /usr/bin
COPY --from=uhd /opt/uhd/share /usr/share

COPY --from=volk /opt/volk/include /usr/include
COPY --from=volk /opt/volk/lib /usr/lib
COPY --from=volk /opt/volk/bin /usr/bin

# Minimal GNU Radio install, to reduce image size. In particular, our installation is headless.
# NOTE: Currently using a custom fork with a one-line patch (see PR: https://github.com/gnuradio/gnuradio/pull/7751),
# because the fix is in the latest maint-3.10 but the cloned OOT modules are not yet compatible with it.
# TODO: Revert to the official GNU Radio maint-3.10 branch once OOT module compatibility is resolved.
RUN git clone --branch v3.10.1.1-streamtag-fix --depth 1 https://github.com/jcfitzpatrick12/gnuradio.git && \
    cd gnuradio && \
    mkdir build && \
    cd build && \
    cmake -Wno-dev \
    -DCMAKE_INSTALL_PREFIX=/opt/gnuradio \
    -DGR_PYTHON_DIR=/opt/gnuradio/lib/python3.10/dist-packages \
    -DENABLE_GNURADIO_RUNTIME=ON \
    -DENABLE_PYTHON=ON \
    -DENABLE_GR_UHD=ON \
    -DENABLE_GR_BLOCKS=ON \
    -DENABLE_GR_FILTER=ON \
    -DENABLE_GR_ANALOG=ON \
    -DENABLE_GR_FFT=ON \
    -DENABLE_GR_UTILS=OFF \
    -DENABLE_GR_MODTOOL=OFF \
    -DENABLE_GR_BLOCKTOOL=OFF \
    -DENABLE_GR_SOAPY=OFF \
    -DENABLE_GR_PDU=OFF \
    -DENABLE_GR_AUDIO=OFF \
    -DENABLE_GR_CHANNELS=OFF \
    -DENABLE_GR_CTRLPORT=OFF \
    -DENABLE_GR_DTV=OFF \
    -DENABLE_GR_FEC=OFF \
    -DENABLE_GR_NETWORK=OFF \
    -DENABLE_GR_QTGUI=OFF \
    -DENABLE_GR_TRELLIS=OFF \
    -DENABLE_GR_VIDEO_SDL=OFF \
    -DENABLE_GR_VOCODER=OFF \
    -DENABLE_GR_ZEROMQ=OFF \
    -DENABLE_MANPAGES=OFF \
    -DENABLE_TESTING=OFF \
    -DENABLE_DOXYGEN=OFF \
    -DENABLE_EXAMPLES=OFF \
    -DENABLE_GRC=OFF \
    .. && \
    make -j"$(nproc)" && \
    make install && \
    rm -rf /tmp/*


# --------------------------------- #
# Install the SDRplay API.
# --------------------------------- #
FROM build AS sdrplay_api

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
    ln --symbolic ${SDRPLAY_API_LIB}.so.${SDRPLAY_API_MAJ_MIN} /opt/sdrplay_api/lib/${SDRPLAY_API_LIB}.so && \
    rm -rf /tmp/*


# --------------------------------------------- #
# Create an executable to find SDRplay devices.
# --------------------------------------------- #
FROM build AS sdrplay_find_devices

WORKDIR /tmp/sdrplay_find_devices

COPY --from=sdrplay_api /opt/sdrplay_api/include/ /usr/include/
COPY --from=sdrplay_api /opt/sdrplay_api/lib/ /usr/lib/
COPY ./scripts/cpp/sdrplay_find_devices.cpp sdrplay_find_devices.cpp

RUN mkdir -p /opt/sdrplay_find_devices/bin && \
    g++ sdrplay_find_devices.cpp -l sdrplay_api -o /opt/sdrplay_find_devices/bin/sdrplay_find_devices && \
    rm -rf /tmp/*


# --------------------------------------------- #
# Install the gr-sdrplay3 OOT module.
# --------------------------------------------- #
FROM build AS gr_sdrplay3

WORKDIR /tmp

COPY --from=sdrplay_api /opt/sdrplay_api/include/ /usr/include/
COPY --from=sdrplay_api /opt/sdrplay_api/lib/ /usr/lib/

COPY --chmod=0755 ./scripts/bash/build_oot_module.sh build_oot_module.sh
RUN . ./build_oot_module.sh && \
    build_from_repo https://github.com/fventuri/gr-sdrplay3.git message-passing && \
    rm -rf /tmp/*


# --------------------------------------------- #
# Install the gr-spectre OOT module.
# --------------------------------------------- #
FROM build AS gr_spectre

WORKDIR /tmp

COPY --chmod=0755 ./scripts/bash/build_oot_module.sh build_oot_module.sh
RUN . ./build_oot_module.sh && \
    build_from_repo https://github.com/jcfitzpatrick12/gr-spectre.git v0.0.4 && \
    rm -rf /tmp/*


# --------------------------------- # 
# Install the spectre server.
# --------------------------------- # 

# Use the `base` stage instead of `build` to avoid copying Python packages needed only for building GNU Radio. 
# Otherwise, since we're not using venvs and everything is installed system wide, these would be copied into the 
# final runtime image later.
FROM base AS spectre_server

# Set up a working directory for the Python build
WORKDIR /tmp/spectre_server

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip && \
    python3 -m pip install --upgrade pip && \
    rm -rf /var/lib/apt/lists/*


# Copy in the source code and build requirements.
COPY pyproject.toml ./
COPY src src

# Finally, install the Python dependencies into the virtual environment.
RUN pip install . && \
    rm -rf /tmp/*

COPY gunicorn.conf.py /opt/spectre_server/


# --------------------------------- # 
# Create the final runtime image.
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
COPY --from=sdrplay_api /opt/sdrplay_api/lib /usr/lib
COPY --from=sdrplay_find_devices /opt/sdrplay_find_devices/bin /usr/bin

# Copy in the UHD runtime dependencies.
COPY --from=uhd /opt/uhd/lib /usr/lib
COPY --from=uhd /opt/uhd/bin /usr/bin
COPY --from=uhd /opt/uhd/share /usr/share

# Copy in the Volk runtime dependencies.
COPY --from=volk /opt/volk/lib /usr/lib
COPY --from=volk /opt/volk/bin /usr/bin

# Copy in the GNU Radio runtime dependencies.
COPY --from=gnuradio /opt/gnuradio/lib /usr/lib
COPY --from=gnuradio /opt/gnuradio/bin /usr/bin
COPY --from=gnuradio /opt/gnuradio/share /usr/share

# Copy in the gr-sdrplay3 OOT module runtime dependencies.
COPY --from=gr_sdrplay3 /opt/gr_sdrplay3/lib/ /usr/lib
COPY --from=gr_sdrplay3 /opt/gr_sdrplay3/local/ /usr/local/

# Copy in the gr-spectre OOT module runtime dependencies.
COPY --from=gr_spectre /opt/gr_spectre/lib/ /usr/lib
COPY --from=gr_spectre /opt/gr_spectre/local/ /usr/local/

# Copy in the spectre server runtime dependencies.
COPY --from=spectre_server /usr/local/lib/python3.10/dist-packages/ /usr/local/lib/python3.10/dist-packages/
COPY --from=spectre_server /opt/spectre_server/gunicorn.conf.py /app/gunicorn.conf.py

# Copy in the scripts which will run when the container starts.
COPY --chmod=0755 scripts/bash/entrypoint.sh entrypoint.sh
COPY --chmod=0755 scripts/bash/cmd.sh cmd.sh

# Add a non-root user to run the application.
RUN useradd -u 1000 -M -d /app appuser

# We cannot use the `USER` directive, since non-root user running the application can't write to the mounted volume,
# or (by default) access USB devices. So, the container starts as root to change ownership of things, then drops 
# privileges and runs as the non-root user to execute the application.
# See https://stackoverflow.com/questions/65574334/docker-is-it-safe-to-switch-to-non-root-user-in-entrypoint for 
# some discussion on this approach.
ENTRYPOINT ["/bin/sh", "entrypoint.sh"]
CMD ["/app/cmd.sh"]


# ----------------------------------------------------------- # 
# Optional target, where you can run the application as root.
# ----------------------------------------------------------- # 
FROM runtime AS root_runtime

# Override inherited entrypoint to allow running as root without privilege drop.
ENTRYPOINT [ ]
CMD ["/app/cmd.sh"]

# --------------------------------- # 
# Create the development stage.
# --------------------------------- # 
FROM runtime AS development

# Broadly copy in all the build dependencies.
COPY --from=build /usr /usr

# Install extra development tools.
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    python3-venv \
    twine && \
    python3 -m pip install --upgrade twine && \  
    rm -rf /var/lib/apt/lists/*

# Clone the `spectre` repository and install the server in editable mode
RUN git clone https://github.com/jcfitzpatrick12/spectre.git --no-checkout && cd spectre && \
    git sparse-checkout init --no-cone && \
    git sparse-checkout set backend/ && \
    git checkout && \
    pip install --editable backend/

# Get the latest version of `spectre-core` and install it in editable mode
RUN git clone https://github.com/jcfitzpatrick12/spectre-core.git && cd spectre-core && \
    pip install --editable .

# Get the latest version of `gr-spectre`.
RUN git clone https://github.com/jcfitzpatrick12/gr-spectre.git
        
# Disable the existing entrypoint and start up commands, and run as root.
ENTRYPOINT [ ]
CMD [ "/bin/bash" ]