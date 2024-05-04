# set SPECTREPARENTPATH to the parent directory of this script
export SPECTREPARENTPATH=$(dirname "$(dirname "$(realpath "$0")")")

# Check if the directory $SPECTREPARENTPATH/chunks exists; if not, create it
if [ ! -d "$SPECTREPARENTPATH/chunks" ]; then
    mkdir "$SPECTREPARENTPATH/chunks"
fi

# Create a volume so that storage persists
docker volume create spectre-host-vol

# Run the Docker container with GUI support
docker run --name spectre-host-container -it --rm \
    --mount type=volume,src=spectre-host-vol,target=/home \
    -v /dev/shm:/dev/shm \
    -v $SPECTREPARENTPATH/chunks:$SPECTREPARENTPATH \
    spectre-host

