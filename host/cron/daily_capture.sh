#!/bin/bash
#Set SPECTREHOST as the parent directory of the package
export SPECTREPARENTPATH=/home/spectre
#add spectre to the python path so we can import modules properly
export PYTHONPATH="${SPECTREPARENTPATH}:${PYTHONPATH}"
# ensure that spectre is recognised as a command in the cron environment
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
# set the display environment variable
export DISPLAY=:0

spectre capture start-watcher -t jool
spectre capture start --receiver RSPDuo --mode tuner_1_fixed --tag jool
sleep 36000s
spectre capture stop