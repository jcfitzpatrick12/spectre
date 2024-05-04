# Create a volume so that storage persists
docker volume create spectre-host-vol

# Run the Docker container with GUI support
docker run --name spectre-host-container -it --rm \
    --mount type=volume,src=spectre-host-vol,target=/home \
    -v /dev/shm:/dev/shm \
    spectre-host

