#Set SPECTREHOST as the parent directory of the package
export SPECTREPARENTPATH=/home/spectre
#add spectre to the python path so we can import modules properly
export PYTHONPATH="${SPECTREPARENTPATH}:${PYTHONPATH}"
# ensure that spectre is recognised as a command in the cron environment
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# ensure the chunks directory is created prior to calling capture
mkdir -p $SPECTREPARENTPATH/host/chunks

spectre print capture-config -t jool
spectre capture start-watcher -t jool
spectre capture start --receiver RSPDuo --mode tuner_1_fixed --tag jool
sleep 36000s
spectre capture stop
