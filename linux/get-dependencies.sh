#!/bin/bash
set -euo pipefail

echo "📦 Installing Ubuntu build dependencies..."

export DEBIAN_FRONTEND=noninteractive

apt update

apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    python3-gi \
    gir1.2-gtk-4.0 \
    libadwaita-1-0 \
    libglib2.0-0 \
    libcairo2 \
    gobject-introspection \
    pkg-config \
    build-essential \
    git \
    wget \
    file \
    binutils \
    fuse3

echo "✅ Ubuntu dependencies installed!"
