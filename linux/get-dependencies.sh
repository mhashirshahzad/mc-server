#!/bin/sh
set -eu

# get-dependencies.sh - For Arch Linux container

# Initialize pacman keyring (needed in fresh containers)
pacman-key --init
pacman-key --populate archlinux

# Update and install
pacman -Sy --noconfirm \
    python \
    python-gobject \
    python-requests \
    python-appdirs \
    gtk4 \
    gtk3 \
    libadwaita \
    gobject-introspection \
    glib2 \
    git \
    base-devel \
    wget \
    file \
    binutils

# For AppImage tools
pacman -S --noconfirm \
    fuse2 \
    fuse3

echo "All dependencies installed!"
