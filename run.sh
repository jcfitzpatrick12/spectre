#create a volume so that storage persists
docker volume create host-spectre-vol

docker run --name spectre-host-container -it --rm \
    --mount type=volume,src=host-spectre-vol,target=/home \
    -v /dev/shm:/dev/shm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    spectre-host