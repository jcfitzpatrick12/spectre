# Set SPECTREPARENTPATH to the parent directory of this script
export SPECTREPARENTPATH=$(dirname "$(dirname "$(realpath "$0")")")

# Check if the directory $SPECTREPARENTPATH/chunks exists; if not, create it
if [ ! -d "$SPECTREPARENTPATH/chunks" ]; then
    mkdir -p "$SPECTREPARENTPATH/chunks"
fi

# Create named volumes for configuration and logs
docker volume create spectre-host-config-vol
docker volume create spectre-host-logs-vol

# Run the Docker container with GUI support
docker run --name spectre-host-container -it --rm \
    -v spectre-host-config-vol:/home/spectre/cfg \
    -v spectre-host-logs-vol:/home/spectre/logs \
    -v $SPECTREPARENTPATH/chunks:/home/spectre/chunks \
    -v /dev/shm:/dev/shm \
    spectre-host
