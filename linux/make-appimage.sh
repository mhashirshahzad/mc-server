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

echo -e "\033[0;33m🔨 Building Grassy AppImage (using sharun)...\033[0m"

# Verify required files exist
if [ ! -f "$ICON" ]; then
    echo -e "\033[0;31m❌ Icon not found at $ICON\033[0m"
    exit 1
fi

if [ ! -f "$DESKTOP" ]; then
    echo -e "\033[0;31m❌ Desktop file not found at $DESKTOP\033[0m"
    exit 1
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
export PYTHONPATH="$HERE/usr/lib/python3/dist-packages:$HERE/usr/lib/python3.12/site-packages"

# Execute the binary built by PyInstaller
exec "$HERE/usr/bin/grassy" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# --- Step 5: Bundle dependencies with quick-sharun ---
echo -e "\033[0;33m📚 Bundling dependencies with quick-sharun...\033[0m"

# Check if quick-sharun is available
if ! command -v quick-sharun >/dev/null 2>&1; then
    echo -e "\033[0;33m⚠️  quick-sharun not found. Installing locally...\033[0m"
    wget -O quick-sharun https://github.com/VHSgunzo/sharun/releases/latest/download/quick-sharun-x86_64.AppImage
    chmod +x quick-sharun
    QUICK_SHARUN="./quick-sharun"
else
    QUICK_SHARUN="quick-sharun"
fi

# Run quick-sharun on the main binary
if [ -f "$APPDIR/usr/bin/grassy" ]; then
    $QUICK_SHARUN "$APPDIR/usr/bin/grassy"
    echo -e "\033[0;32m✅ Dependencies bundled\033[0m"
else
    echo -e "\033[0;31m❌ Binary not found at $APPDIR/usr/bin/grassy\033[0m"
    exit 1
fi

# --- Step 6: Generate the final AppImage ---
echo -e "\033[0;33m📀 Creating AppImage...\033[0m"

# Build the AppImage
$QUICK_SHARUN --make-appimage

# --- Step 7: Organize output ---
mkdir -p "$RELEASE_DIR"

# Find and rename the AppImage to simple name
if ls *.AppImage 1>/dev/null 2>&1; then
    for appimage in *.AppImage; do
        mv "$appimage" "$RELEASE_DIR/$FINAL_NAME"
        echo -e "\033[0;32m✅ AppImage created: $RELEASE_DIR/$FINAL_NAME\033[0m"
        ls -lh "$RELEASE_DIR/$FINAL_NAME"
    done
else
    echo -e "\033[0;31m❌ Failed to create AppImage\033[0m"
    exit 1
fi

# Also handle zsync file if exists
if ls *.zsync 1>/dev/null 2>&1; then
    mv *.zsync "$RELEASE_DIR/" 2>/dev/null || true
fi

# --- Step 8: Cleanup build artifacts (optional) ---
echo -e "\033[0;33m🧹 Cleaning up...\033[0m"
rm -rf "$BUILD_DIR" 2>/dev/null || true
rm -rf "$APPDIR" 2>/dev/null || true

echo -e "\033[0;32m✅ Build complete! AppImage is in $RELEASE_DIR/$FINAL_NAME\033[0m"
