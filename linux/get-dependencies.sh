#!/bin/sh
set -eu

echo "📦 installing minimal arch build deps for AppImage..."

pacman -Sy --noconfirm \
    python \
    python-pip \
    python-requests \
    python-appdirs \
    python-gobject \
    gtk4 \
    libadwaita \
    gobject-introspection \
    glib2 \
    base-devel \
    git \
    wget \
    file \
    binutils \
    fuse3 \
    # Additional deps for AppImage
    libfuse2 \
    desktop-file-utils \
    libappimage

echo "✅ done"
