#!/bin/bash

# Private: Fix an apparent bug installing OOT modules on ubuntu.
file_fix() {
    mv "/usr/local/lib/$(uname -m)-linux-gnu/"* "/usr/lib/$(uname -m)-linux-gnu/"
}

# Public: Build a GNU Radio OOT module from a GitHub repository.
#
# $1 - The repository URL.
# $2 - The branch or tag to checkout.
build_from_repo() {
    local repo_url=$1
    local branch_or_tag=$2
    # Extract the repository name from the URL.
    local repo_name=$(basename "$repo_url" .git)

    # Clone the repository.
    git clone "$repo_url"
    # Change directory into the newly cloned repository.
    cd "$repo_name"
    # Checkout the requested branch or tag.
    git checkout "$branch_or_tag"

    # Build the OOT module.
    mkdir build && cd build
    cmake .. && make
    sudo make install

    # Run the file fix
    # file_fix
}
