#!/bin/bash
# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# -----------------------------------------------------------------------------
# Why is this script so chatty?
# Spectre welcomes folks who may be new to Linux tooling. Instead of silently
# mutating your system, we announce each step, explain *why* we need it, and
# celebrate when it succeeds. When elevated privileges are required (e.g. to
# write udev rules), we call that out so nothing feels mysterious. Run it once,
# read along, and you will know exactly what changed.
# -----------------------------------------------------------------------------

# Server-side environment variables.
SPECTRE_BIND_HOST="0.0.0.0"
SPECTRE_BIND_PORT="5000"
SPECTRE_PORT_MAP="127.0.0.1:5000:5000"

# Client-side environment variables.
SPECTRE_SERVER_HOST="spectre-server"
SPECTRE_SERVER_PORT="5000"

echo "👋 Welcome! This helper will prep Linux so Spectre can talk to your SDR hardware."
echo "We'll create a USB access group, install udev rules, and drop a .env file for Docker."
echo "Heads-up: some steps need administrator powers, so you'll run this via sudo."

# Check if the script is run with root privileges.
if [ "$EUID" -ne 0 ]; then
    echo "I can't continue without root access. Please run: sudo ./setup.sh"
    exit 1
fi

read -rp "Ready to continue? (Y/n) " CONFIRM
CONFIRM=${CONFIRM:-Y}
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "No worries. Re-run this script whenever you're ready."
    exit 0
fi

PRIMARY_USER=${SUDO_USER:-}
NEED_RELOGIN=false

# Quick pre-flight checks so troubleshooting stays minimal.
echo "Checking that Docker is installed and running..."
if ! command -v docker > /dev/null; then
    echo "I couldn't find the 'docker' command. Install Docker Desktop/Engine, then re-run this setup."
    exit 1
fi

if ! timeout 5 docker info > /dev/null 2>&1; then
    echo "Docker seems to be unavailable or not running. Start Docker and re-run this script."
    exit 1
fi
echo "Success! Docker engine responded."

echo "Checking for the Docker Compose plugin..."
if ! docker compose version > /dev/null 2>&1; then
    echo "I couldn't detect 'docker compose'. Install the Compose plugin (or Docker Desktop) before continuing."
    exit 1
fi
echo "Success! Docker Compose is ready."

echo "Creating a shared group so Docker containers can reach your USB SDRs..."
SPECTRE_GROUP=spectre-group
if getent group "$SPECTRE_GROUP" > /dev/null; then
    echo "Group '$SPECTRE_GROUP' already exists — skipping creation."
else
    groupadd "$SPECTRE_GROUP"
    echo "Success! Added group '$SPECTRE_GROUP'."
fi
SPECTRE_GID=$(getent group "$SPECTRE_GROUP" | cut -d: -f3)

# Allow users in the group to access USB devices from named vendors.
echo "Writing udev rules so Linux spots your SDR hardware without sudo..."
if ! command -v udevadm > /dev/null; then
    echo "I can't find 'udevadm'. Install udev (or run this on a distro with udev) before proceeding."
    exit 1
fi
UDEV_FILE="/etc/udev/rules.d/99-spectre.rules"
{
    echo '# Ettus Research'
    echo "SUBSYSTEM==\"usb\", ENV{ID_VENDOR_ID}==\"2500\", MODE=\"0660\", GROUP=\"$SPECTRE_GROUP\""
    echo "# SDRplay"
    echo "SUBSYSTEM==\"usb\", ENV{ID_VENDOR_ID}==\"1df7\", MODE=\"0660\", GROUP=\"$SPECTRE_GROUP\""
    echo '# HackRF'
    echo "SUBSYSTEM==\"usb\", ENV{ID_VENDOR_ID}==\"1d50\", MODE=\"0660\", GROUP=\"$SPECTRE_GROUP\""
    echo '# RTL-SDR'
    echo "SUBSYSTEM==\"usb\", ENV{ID_VENDOR_ID}==\"0bda\", MODE=\"0660\", GROUP=\"$SPECTRE_GROUP\""
} > "$UDEV_FILE"
echo "Success! Rules saved to $UDEV_FILE."

# Apply the new udev rules.
echo "Reloading udev so the new permissions kick in..."
udevadm control --reload-rules
udevadm trigger
echo "Success! USB rules refreshed."

# Friendly reminder if no supported SDR is connected yet.
if command -v lsusb > /dev/null; then
    if ! lsusb | grep -E -q '(2500|1df7|1d50|0bda)'; then
        echo "(Optional) No known SDR devices detected right now. That's fine—you can plug them in later and rerun this script to refresh udev."
    fi
else
    echo "Note: 'lsusb' not found, so I can't auto-detect connected SDRs."
fi

# Write environment variables to the `.env` file, which will be used to interpolate the docker compose configs.
DOTENV_FILE="./.env"
echo "Documenting container settings in $DOTENV_FILE so Docker Compose stays happy..."
# Offer to back up an existing .env file.
if [ -f "$DOTENV_FILE" ]; then
    BACKUP_NAME="${DOTENV_FILE}.backup.$(date +%Y%m%d%H%M%S)"
    read -rp "Found an existing $DOTENV_FILE. Create a backup before overwriting? (Y/n) " BACKUP_CONFIRM
    BACKUP_CONFIRM=${BACKUP_CONFIRM:-Y}
    if [[ $BACKUP_CONFIRM =~ ^[Yy]$ ]]; then
        cp "$DOTENV_FILE" "$BACKUP_NAME"
        echo "Backed up previous env file to $BACKUP_NAME."
    else
        echo "Skipping backup at your request."
    fi
fi
{
    echo "SPECTRE_GID=$SPECTRE_GID"
    echo "SPECTRE_BIND_HOST=$SPECTRE_BIND_HOST"
    echo "SPECTRE_BIND_PORT=$SPECTRE_BIND_PORT"
    echo "SPECTRE_PORT_MAP=$SPECTRE_PORT_MAP"
    echo "SPECTRE_SERVER_HOST=$SPECTRE_SERVER_HOST"
    echo "SPECTRE_SERVER_PORT=$SPECTRE_SERVER_PORT"
} > "$DOTENV_FILE"
echo "Success! Environment file written."

# Ensure the Docker socket has the expected ownership.
if [ -S /var/run/docker.sock ]; then
    SOCKET_GRP=$(stat -c "%G" /var/run/docker.sock)
    if [ "$SOCKET_GRP" != "docker" ]; then
        echo "FYI: /var/run/docker.sock is owned by group '$SOCKET_GRP'."
        echo "If 'docker compose up' still needs sudo later, restart Docker or adjust the socket permissions."
    fi
fi

# Ensure the invoking user can run Docker commands without sudo.
echo "Double-checking your Docker permissions so future commands run smoothly..."
if ! getent group docker > /dev/null; then
    echo "It looks like the 'docker' group does not exist yet. Install Docker first, then re-run this step."
elif [ -z "$PRIMARY_USER" ] || [ "$PRIMARY_USER" = "root" ]; then
    echo "Skipping user enrollment because you're running directly as root."
else
    if id -nG "$PRIMARY_USER" | grep -qw docker; then
        echo "Great news: $PRIMARY_USER is already in the docker group."
    else
        usermod -aG docker "$PRIMARY_USER"
        NEED_RELOGIN=true
        echo "Success! Added $PRIMARY_USER to the docker group so 'docker compose up' works without sudo."
    fi
fi

echo
echo "✨ Setup complete!"
echo "Next up: plug in your SDR (if you have one) and run 'docker compose up'."
if [ "$NEED_RELOGIN" = true ]; then
    echo "Heads up: log out and back in (or reboot) so your new docker permissions stick."
fi
echo "Thanks for letting me walk you through the Linux bits."
