#!/bin/bash

# Public: Build a GNU Radio OOT module from a GitHub repository.
#
# $1 - The repository URL.
# $2 - The branch or tag to checkout.
build_from_repo() {
    local repo_url=$1
    local branch_or_tag=$2
    
    # Extract the repository name from the URL.
    local repo_name=$(basename "$repo_url" .git)

    # Clone the repository, and navigate to its root directory.
    git clone --branch "$branch_or_tag" --depth 1 "$repo_url" && cd "$repo_name"

    # Build the OOT module.
    mkdir build && cd build

    # Replace hyphens with underscores in the repo name.
    local repo_name=$(echo "$repo_name" | tr '-' '_')
    cmake -DCMAKE_INSTALL_PREFIX=/opt/${repo_name} ..
    make && make install

    # Return to the original directory
    cd ../..
}
