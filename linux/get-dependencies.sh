#!/bin/sh
set -eu

echo "📦 installing minimal arch build deps..."

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
    fuse3

echo "✅ done"
