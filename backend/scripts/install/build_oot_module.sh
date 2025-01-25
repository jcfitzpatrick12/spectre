#!/bin/bash
# build_repo.sh - Defines the build_repo function


file_fix() {
    mv "/usr/local/lib/$(uname -m)-linux-gnu/"* "/usr/lib/$(uname -m)-linux-gnu/"
}

build_repo() {
    local repo_url=$1
    local branch_or_tag=$2
    local repo_name=$(basename "$repo_url" .git)

    git clone "$repo_url"
    cd "$repo_name" || exit
    git checkout "$branch_or_tag"
    mkdir build && cd build
    cmake .. && make
    sudo make install
    cd ../..
    file_fix
}
