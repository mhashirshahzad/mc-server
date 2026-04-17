
#!/bin/sh
set -eu

# Update package database and install required system packages
pacman -Syu --noconfirm \
    python \
    python-pip \
    python-gobject \
    python-requests \
    python-appdirs \
    gtk4 \
    libadwaita \
    gobject-introspection \
    pkgconf \
    git \
    base-devel

# Install any extra Python packages from requirements.txt (if not already covered by pacman)

# this breaks dont do this
# pip install --no-cache-dir -r requirements.txt

echo "All dependencies installed successfully."
