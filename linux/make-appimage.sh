#!/bin/sh
set -eu

# --- Configuration ---
BINARY_NAME="grassy"
RELEASE_DIR="release"
APPDIR="$RELEASE_DIR/Grassy.AppDir"
BUILD_DIR="$RELEASE_DIR/build"
DIST_DIR="$RELEASE_DIR/dist"

# --- Simple fixed name (no version) ---
ARCH=$(uname -m)
FINAL_NAME="${BINARY_NAME}-${ARCH}.AppImage"

export OUTPATH="./dist"

# --- Metadata (Both files are in assets/) ---
export ICON="$(pwd)/assets/icon.png"
export DESKTOP="$(pwd)/assets/grassy.desktop"

# --- AppImageTool path ---
APPIMAGETOOL="$(pwd)/appimagetool-x86_64.AppImage"

echo -e "\033[0;33m🔨 Building Grassy AppImage (using appimagetool)...\033[0m"

# Verify required files exist
if [ ! -f "$ICON" ]; then
    echo -e "\033[0;31m❌ Icon not found at $ICON\033[0m"
    exit 1
fi

if [ ! -f "$DESKTOP" ]; then
    echo -e "\033[0;31m❌ Desktop file not found at $DESKTOP\033[0m"
    exit 1
fi

# Verify appimagetool exists
if [ ! -f "$APPIMAGETOOL" ]; then
    echo -e "\033[0;31m❌ appimagetool not found at $APPIMAGETOOL\033[0m"
    echo -e "\033[0;33m⚠️  Downloading appimagetool...\033[0m"
    wget -O "$APPIMAGETOOL" https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x "$APPIMAGETOOL"
fi

# --- Step 1: Create virtual environment and install dependencies ---
echo -e "\033[0;33m📦 Setting up Python environment...\033[0m"

# Use a temporary venv in the build directory
VENV_DIR="$BUILD_DIR/venv"
python3 -m venv "$VENV_DIR" --clear
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r requirements.txt

# Install PyInstaller
"$VENV_DIR/bin/pip" install pyinstaller

# --- Step 2: Build with PyInstaller ---
echo -e "\033[0;33m📦 Building PyInstaller bundle...\033[0m"

"$VENV_DIR/bin/python" -m PyInstaller \
    --name "$BINARY_NAME" \
    --onedir \
    --windowed \
    --distpath "$DIST_DIR" \
    --workpath "$BUILD_DIR/pyinstaller" \
    --specpath "$BUILD_DIR" \
    --hidden-import=gi \
    --hidden-import=gi.repository.Gtk \
    --hidden-import=gi.repository.Adw \
    --hidden-import=requests \
    --hidden-import=appdirs \
    src/main.py

# --- Step 3: Prepare AppDir structure ---
echo -e "\033[0;33m📁 Creating AppDir structure...\033[0m"

rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# Copy PyInstaller bundle
cp -r "$DIST_DIR/$BINARY_NAME"/* "$APPDIR/usr/bin/"

# Copy desktop file (from assets/)
cp "$DESKTOP" "$APPDIR/grassy.desktop"
cp "$DESKTOP" "$APPDIR/usr/share/applications/"

# Copy icon from assets/ to all required locations
cp "$ICON" "$APPDIR/grassy.png"
cp "$ICON" "$APPDIR/usr/share/icons/hicolor/256x256/apps/grassy.png"
cp "$ICON" "$APPDIR/.DirIcon"

# --- Step 4: Create AppRun wrapper ---
echo -e "\033[0;33m🚀 Creating AppRun wrapper...\033[0m"

cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "$0")")"
export PATH="$HERE/usr/bin:$PATH"
export LD_LIBRARY_PATH="$HERE/usr/lib:$LD_LIBRARY_PATH"
export GI_TYPELIB_PATH="$HERE/usr/lib/girepository-1.0:$GI_TYPELIB_PATH"

# Execute the binary built by PyInstaller
exec "$HERE/usr/bin/grassy" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# --- Step 5: Build AppImage with appimagetool ---
echo -e "\033[0;33m📀 Creating AppImage with appimagetool...\033[0m"

# Make appimagetool executable
chmod +x "$APPIMAGETOOL"

# Build the AppImage (using zstd compression for faster startup)
"$APPIMAGETOOL" \
    --comp zstd \
    --mksquashfs-opt "-Xcompression-level 6" \
    --mksquashfs-opt "-b 131072" \
    "$APPDIR" \
    "$FINAL_NAME"

# --- Step 6: Organize output ---
mkdir -p "$RELEASE_DIR"

# Move AppImage to release directory
if [ -f "$FINAL_NAME" ]; then
    mv "$FINAL_NAME" "$RELEASE_DIR/"
    echo -e "\033[0;32m✅ AppImage created: $RELEASE_DIR/$FINAL_NAME\033[0m"
    ls -lh "$RELEASE_DIR/$FINAL_NAME"
else
    echo -e "\033[0;31m❌ Failed to create AppImage\033[0m"
    exit 1
fi

# Also handle zsync file if exists
if ls *.zsync 1>/dev/null 2>&1; then
    mv *.zsync "$RELEASE_DIR/" 2>/dev/null || true
fi

# --- Step 7: Cleanup build artifacts ---
echo -e "\033[0;33m🧹 Cleaning up...\033[0m"
rm -rf "$BUILD_DIR" 2>/dev/null || true
rm -rf "$APPDIR" 2>/dev/null || true

echo -e "\033[0;32m✅ Build complete! AppImage is in $RELEASE_DIR/$FINAL_NAME\033[0m"
