#!/bin/bash

# Update the shared library cache
ldconfig

# Start the SDRPlay API service as a background process
/opt/sdrplay_api/sdrplay_apiService &

# Start the spectre server
python3.10 -m spectre_server