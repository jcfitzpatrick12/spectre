#!/bin/bash
# Define source and destination directories
source_dir="/usr/local/lib/x86_64-linux-gnu"
dest_dir="/usr/lib/x86_64-linux-gnu"
# Move files
mv "${source_dir}/libgnuradio-sdrplay3.so."* "${dest_dir}/"

