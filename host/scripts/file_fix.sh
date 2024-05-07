#!/bin/bash

######## Note ##########
# file fix is required on both raspberry pi and standard x86 architectures
# but the directory where we need to move the files from is system dependent
# this script detects the architecture and changes the suffix directory dynamically
########################


# Function to determine architecture-specific directory suffix
get_lib_dir_suffix() {
    case "$(uname -m)" in
        x86_64)
            echo "x86_64-linux-gnu"
            ;;
        aarch64)
            echo "aarch64-linux-gnu"
            ;;
        *) 
            echo "unsupported-architecture"
            echo "Unsupported architecture. Exiting script."
            exit 1
            ;;
    esac
}

# Define architecture-specific part of the directory name
lib_dir_suffix=$(get_lib_dir_suffix)

# Define source and destination directories
source_dir="/usr/local/lib/${lib_dir_suffix}"
dest_dir="/usr/lib/${lib_dir_suffix}"

# Move files
mv "${source_dir}/"* "${dest_dir}/"
