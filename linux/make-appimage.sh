#!/bin/sh
set -eu

ARCH=$(uname -m)
# Handle git describe failure when not in git repo
if git describe --tags --always 2>/dev/null; then
    VERSION=$(git describe --tags --always)
else
    VERSION="dev"
fi
export ARCH VERSION
export OUTPATH=./dist
export ADD_HOOKS="self-updater.hook"
export UPINFO="gh-releases-zsync|${GITHUB_REPOSITORY%/*}|${GITHUB_REPOSITORY#*/}|latest|*$ARCH.AppImage.zsync"

# --- Required metadata (Using your actual files) ---
# Convert PNG to SVG or use PNG directly (AppImage works with PNG too)
export ICON="$(pwd)/assets/icon.png"
export DESKTOP="$(pwd)/grassy.desktop"

# Check if required files exist
if [ ! -f "$ICON" ]; then
    echo "ERROR: Icon not found at $ICON"
    exit 1
fi
if [ ! -f "$DESKTOP" ]; then
    echo "ERROR: Desktop file not found at $DESKTOP"
    exit 1
fi

# --- Deployment options ---
export DEPLOY_PYTHON=1
export DEPLOY_GTK=1
export GTK_DIR=gtk-4.0
export DEPLOY_LOCALE=1
export STARTUPWMCLASS=io.github.yourusername.grassy
export GTK_CLASS_FIX=1

# --- Create AppDir structure ---
mkdir -p ./AppDir/usr/bin
mkdir -p ./AppDir/usr/lib
mkdir -p ./AppDir/usr/share
mkdir -p ./AppDir/usr/share/icons/hicolor/scalable/apps
mkdir -p ./AppDir/usr/share/applications

# Copy your icon and desktop file into AppDir
cp "$ICON" ./AppDir/usr/share/icons/hicolor/scalable/apps/grassy.png
cp "$DESKTOP" ./AppDir/usr/share/applications/

# --- List all binaries and data your app needs ---
quick-sharun /usr/bin/grassy \
    /usr/lib/python3.*/site-packages/grassy \
    /usr/share/grassy \
    /usr/lib/libgobject* \
    /usr/lib/libglib* \
    /usr/lib/libgtk* \
    /usr/lib/libadwaita* \
    /usr/lib/girepository* \
    /usr/lib/libgirepository*

# --- If your app is a single Python script (not installed system-wide) ---
# First check if your script exists
if [ -f "./grassy.py" ]; then
    # Copy your script and any local modules into AppDir
    cp ./grassy.py ./AppDir/bin/grassy
    chmod +x ./AppDir/bin/grassy

    # Create a wrapper script that runs Python with the correct environment
    cat << 'EOF' > ./AppDir/AppRun
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
export PYTHONPATH="${HERE}/usr/lib/python3.12/site-packages:${PYTHONPATH:-}"
exec "${HERE}/bin/python3" "${HERE}/bin/grassy" "$@"
EOF
    chmod +x ./AppDir/AppRun
elif [ -f "./src/grassy.py" ]; then
    # Alternative location
    cp ./src/grassy.py ./AppDir/bin/grassy
    chmod +x ./AppDir/bin/grassy
    # ... (rest of wrapper creation)
else
    echo "WARNING: grassy.py not found in current directory or ./src/"
fi

# --- Turn AppDir into AppImage ---
quick-sharun --make-appimage

# --- Test the final app ---
if ls ./dist/*.AppImage 1>/dev/null 2>&1; then
    quick-sharun --test ./dist/*.AppImage
else
    echo "ERROR: No AppImage found in ./dist/"
    exit 1
fi
