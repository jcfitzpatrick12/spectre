# Use an Ubuntu image
FROM ubuntu:22.04

# stop interactive dialogue (only for the duration of the build)
ARG DEBIAN_FRONTEND=noninteractive

#Set SPECTREHOST as the parent directory of the package
ENV SPECTREHOSTPARENTPATH /home/host-spectre
#add grso to the python path so we can import modules properly
ENV PYTHONPATH "${PYTHONPATH}:/home/host-spectre"

# Install the required packages for the installation
# versions are most recent as of 13th of March 2024
RUN apt-get update -y && \
    apt-get install -y sudo \
    bash=5.1-6ubuntu1 \
    expect=5.45.4-2build1 \
    git=1:2.34.1-1ubuntu1.10 \
    swig=4.0.2-1ubuntu1 \
    cmake=3.22.1-1ubuntu1.22.04.2 \
    gnuradio=3.10.1.1-2 \
    python3-pip=22.0.2+dfsg-1ubuntu0.4 \
    cron=3.0pl1-137ubuntu3 \
    wget \
    vim && rm -rf /var/lib/apt/lists/*

# download the SDRplay RSP API (fixed version as of 13th March 2024)
RUN wget https://www.sdrplay.com/software/SDRplay_RSP_API-Linux-3.14.0.run
# Copy expect script into image [this will run the API .run and auto accepts any interactive dialogue]
COPY ./scripts/install_RSP_API.sh tmp/install_RSP_API.sh
RUN chmod +x /tmp/install_RSP_API.sh && \
	/tmp/install_RSP_API.sh  && rm tmp/install_RSP_API.sh

# Now copy the script which will install fventuri's gr-sdrplay3 OOT module
COPY ./scripts/install_gr_sdrplay3.sh /tmp/install_gr_sdrplay3.sh
RUN chmod +x /tmp/install_gr_sdrplay3.sh && \ 
    /tmp/install_gr_sdrplay3.sh && rm /tmp/install_gr_sdrplay3.sh
    
# nown fix see https://sdrplayusers.net/forums/topic/problem-sdrplay-with-gnu-radio-3-10-1-installed-via-ubuntu-22-04/
COPY ./scripts/file_fix.sh /tmp/file_fix.sh
RUN chmod +x /tmp/file_fix.sh && \
    /tmp/file_fix.sh && rm /tmp/file_fix.sh


WORKDIR /home
# now clone the spectre-host repository
RUN git clone https://github.com/jcfitzpatrick12/spectre-host.git

COPY ./scripts/startup.sh /startup.sh
RUN chmod +x /startup.sh

CMD ["/startup.sh"]