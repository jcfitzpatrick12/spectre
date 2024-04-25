# Use an Ubuntu image
FROM ubuntu:22.04

# stop interactive dialogue (only for the duration of the build)
ARG DEBIAN_FRONTEND=noninteractive

# Set the DISPLAY environment variable to specify the X server to use for GUI applications.
# This is necessary for running applications with graphical interfaces in some Docker configurations.
ENV DISPLAY=:0

# Set the XDG_RUNTIME_DIR environment variable to define the base directory for user-specific non-essential runtime files and objects.
# This helps prevent warnings about XDG_RUNTIME_DIR not being set and ensures proper operation of applications relying on this standard.
ENV XDG_RUNTIME_DIR=/tmp/runtime-root
#to suppress a warning while loading up gnuradio
ENV NO_AT_BRIDGE=1

#Set SPECTREHOST as the parent directory of the package
ENV SPECTREPARENTPATH /home/spectre
#add spectre to the python path so we can import modules properly
ENV PYTHONPATH "${SPECTREPARENTPATH}:${PYTHONPATH}"


# Install the required packages for the installation
# versions are most recent as of 13th of March 2024
RUN apt-get update -y && \
    apt-get install -y sudo \
    bash=5.1-6ubuntu1.1 \
    # expect is used while installing the RSP API (auto accepts licence agreement etc.)
    expect=5.45.4-2build1 \
    git=1:2.34.1-1ubuntu1.10 \
    # cmake is required for installing OOT modules for gnuradio
    cmake=3.22.1-1ubuntu1.22.04.2 \
    gnuradio=3.10.1.1-2  \
    python3-pip=22.0.2+dfsg-1ubuntu0.4 \
    cron=3.0pl1-137ubuntu3 \
    # lbgtk-3-dev and x11-apps are required for the gnuradio GUI to run inside the container
    libgtk-3-dev=3.24.33-1ubuntu2\
    x11-apps=7.7+8build2 \
    wget=1.21.2-2ubuntu1 \
    # libcanberra packages are installed to subdue some warnings flagged on starting gnuradio-companion
    libcanberra-gtk-module=0.30-10ubuntu1.22.04.1 \
    libcanberra-gtk3-module=0.30-10ubuntu1.22.04.1 \
    # dbus x11 stops a warning when "opening from file" in gnuradio
    dbus-x11=1.12.20-2ubuntu4.1 \
    vim && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

# download the SDRplay RSP API (fixed version as of 13th March 2024)
RUN wget https://www.sdrplay.com/software/SDRplay_RSP_API-Linux-3.14.0.run
# Copy expect script into image [this will run the API .run and auto accepts any interactive dialogue]
COPY ./scripts/install_RSP_API.sh /install_RSP_API.sh
RUN chmod +x /install_RSP_API.sh && \
	/install_RSP_API.sh  && rm /install_RSP_API.sh
# delete the API run file after installation
RUN rm SDRplay_RSP_API-Linux-3.14.0.run

# Now copy the script which will install fventuri's gr-sdrplay3 OOT module
COPY ./scripts/install_gr_sdrplay3.sh /install_gr_sdrplay3.sh
RUN chmod +x /install_gr_sdrplay3.sh && \ 
    /install_gr_sdrplay3.sh && rm /install_gr_sdrplay3.sh

# Now copy the script which will install the gr-spectre custom OOT module
COPY ./scripts/install_gr_spectre.sh /install_gr_spectre.sh
RUN chmod +x /install_gr_spectre.sh && \ 
    /install_gr_spectre.sh && rm /install_gr_spectre.sh
    
# own fix see https://sdrplayusers.net/forums/topic/problem-sdrplay-with-gnu-radio-3-10-1-installed-via-ubuntu-22-04/
COPY ./scripts/file_fix.sh /file_fix.sh
RUN chmod +x /file_fix.sh && \
    /file_fix.sh && rm /file_fix.sh

# install a default crontab
WORKDIR /etc/cron.d
COPY ./cron/default_crontab ./default_crontab
RUN crontab ./default_crontab

WORKDIR /home

# now clone the spectre repository
RUN git clone https://github.com/jcfitzpatrick12/spectre.git && \
    cd spectre/host/ && \
    pip install -r requirements.txt

# Create an alias for running the script
#RUN echo 'alias spectre="python3 -m cli"' >> ~/.bashrc

# making "spectre" cli command  callable from anywhere (from non-interactice shells too!) 
RUN echo '#!/bin/bash' > /usr/local/bin/spectre \
    && echo 'python3 -m host.cli "$@"' >> /usr/local/bin/spectre \
    && chmod +x /usr/local/bin/spectre


COPY ./scripts/startup.sh /usr/local/bin/startup.sh
RUN chmod +x /usr/local/bin/startup.sh

WORKDIR /home/spectre/

ENTRYPOINT ["/usr/local/bin/startup.sh"]
