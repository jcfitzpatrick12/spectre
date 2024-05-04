# Enable xhost for the local machine only, safer than 'xhost +'
xhost local:

# Create a volume so that storage persists
docker volume create spectre-host-vol

# Run the Docker container with GUI support
docker run --name spectre-host-container -it --rm \
    --mount type=volume,src=spectre-host-vol,target=/home \
    -v /dev/shm:/dev/shm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    spectre-host

# Reset xhost
xhost -
