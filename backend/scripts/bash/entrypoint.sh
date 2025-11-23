#!/bin/bash
# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# Create the named `spectre-group` inside the container.
if ! getent group "$SPECTRE_GID" >/dev/null; then
    echo "Creating group 'spectre-group' inside container with GID $SPECTRE_GID"
    groupadd -g "$SPECTRE_GID" spectre-group
fi

# Add out non-root user to the `spectre-group`, so that it can access USB devices.
usermod -aG spectre-group appuser

# Change ownership of the /app directory (including the mounted volume) so that our non-root user can write to it.
chown -R appuser:spectre-group /app

# Seed default configuration profiles if configs directory is empty or missing profiles
CONFIGS_DIR="/app/.spectre-data/configs"
PROFILES_DIR="/app/default_profiles"

if [ -d "$PROFILES_DIR" ]; then
    echo "Checking for default configuration profiles..."

    # Create configs directory if it doesn't exist
    mkdir -p "$CONFIGS_DIR"

    # Count existing config files
    EXISTING_CONFIGS=$(find "$CONFIGS_DIR" -maxdepth 1 -name "*.json" | wc -l)

    # Seed default profiles
    SEEDED_COUNT=0
    for profile in "$PROFILES_DIR"/*.json; do
        if [ -f "$profile" ]; then
            filename=$(basename "$profile")

            # Skip metadata files (not actual receiver configs)
            if [ "$filename" = "profiles_manifest.json" ]; then
                continue
            fi

            dest="$CONFIGS_DIR/$filename"

            # Only copy if file doesn't exist (preserve user modifications)
            if [ ! -f "$dest" ]; then
                cp "$profile" "$dest"
                echo "  Seeded default profile: $filename"
                SEEDED_COUNT=$((SEEDED_COUNT + 1))
            fi
        fi
    done

    if [ $SEEDED_COUNT -gt 0 ]; then
        echo "Successfully seeded $SEEDED_COUNT default configuration profile(s)"
    else
        echo "All default profiles already exist (total configs: $EXISTING_CONFIGS)"
    fi

    # Set ownership for seeded files
    chown -R appuser:spectre-group "$CONFIGS_DIR"
else
    echo "Warning: Default profiles directory not found at $PROFILES_DIR"
fi

# Drop root privileges when running the application.
exec gosu appuser "$@"