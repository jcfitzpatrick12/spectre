# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Use an Ubuntu image (exact version of 22.04)
FROM ubuntu@sha256:3d1556a8a18cf5307b121e0a98e93f1ddf1f3f8e092f1fddfd941254785b95d7

# -------------------------------------------------- # 
# Setting environment variables ...                  #
# -------------------------------------------------- # 

# stop interactive dialogue (only for the duration of the build)
ARG DEBIAN_FRONTEND=noninteractive
# define the spectre data directory path as an environment variable inside the container
ENV SPECTRE_DATA_DIR_PATH="/home/spectre/spectre-data/"

# -------------------------------------------------- # 
# Installing container packages ...                  #
# -------------------------------------------------- # 

# Install the required packages for the installation
RUN apt-get update -y && \
    apt-get install -y sudo \
    # expect is used while installing the RSP API (auto accepts licence agreement etc.)
    expect=5.45.4-2build1 \
    # git is required to clone the GNU Radio OOT module repositories.
    git=1:2.34.1-1ubuntu1.11 \
    # cmake is required for installing OOT modules for gnuradio
    cmake=3.22.1-1ubuntu1.22.04.2 \
    gnuradio=3.10.1.1-2  \
    python3-pip=22.0.2+dfsg-1ubuntu0.5 \
    cron=3.0pl1-137ubuntu3 \
    wget=1.21.2-2ubuntu1.1 \
    vim \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------------- # 
# Installing GNU Radio OOT modules ...               #
# -------------------------------------------------- # 

WORKDIR /tmp

# download the SDRplay RSP API (fixed version)
RUN wget https://www.sdrplay.com/software/SDRplay_RSP_API-Linux-3.15.2.run
# Copy expect script into image [this will run the API .run and auto accepts any interactive dialogue]
COPY scripts/installation/RSP_API.sh RSP_API.sh
RUN chmod +x RSP_API.sh && \
	./RSP_API.sh  &&  \
    rm RSP_API.sh && \
    rm SDRplay_RSP_API-Linux-3.15.2.run

# Now copy the script which will install fventuri's gr-sdrplay3 OOT module
COPY scripts/installation/gr_sdrplay3.sh gr_sdrplay3.sh
RUN chmod +x gr_sdrplay3.sh && \ 
    ./gr_sdrplay3.sh && \
    rm gr_sdrplay3.sh && \
    rm -rf gr-sdrplay

# Now copy the script which will install the gr-spectre custom OOT module
COPY scripts/installation/gr_spectre.sh gr_spectre.sh
RUN chmod +x gr_spectre.sh && \ 
    ./gr_spectre.sh && \
    rm gr_spectre.sh && \
    rm -rf gr-spectre
    
# File fix see https://sdrplayusers.net/forums/topic/problem-sdrplay-with-gnu-radio-3-10-1-installed-via-ubuntu-22-04/
COPY scripts/installation/file_fix.sh file_fix.sh
RUN chmod +x file_fix.sh && \
    ./file_fix.sh && \
    rm file_fix.sh


# -------------------------------------------------- # 
# Installing spectre backend ...                     #
# -------------------------------------------------- # 
WORKDIR /home
COPY scripts/installation/spectre_backend.sh spectre_backend.sh
RUN chmod +x spectre_backend.sh && \ 
    ./spectre_backend.sh && \
    rm spectre_backend.sh

# -------------------------------------------------- # 
# Configuring cron jobs ...                          #
# -------------------------------------------------- # 

# # Copy the default crontab file to the cron.d directory
# WORKDIR /etc/cron.d
# # copy in the default crontab
# COPY scripts/cron/default_crontab default_crontab
# # install the crontab
# RUN crontab default_crontab
# # Copy the daily capture scripts
# COPY scripts/cron/daily_capture.sh /home/cron/daily_capture.sh


# -------------------------------------------------- # 
# Final set-up ...                                   #
# -------------------------------------------------- # 
# ENTRYPOINT ["python3", "/home/spectre/backend/src/spectre_server/main.py"]
