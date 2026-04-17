#!/bin/bash
set -euo pipefail

# --- Configuration ---
BINARY_NAME="grassy"
RELEASE_DIR="release"
APPDIR="$RELEASE_DIR/Grassy.AppDir"
BUILD_DIR="$RELEASE_DIR/build"
DIST_DIR="$RELEASE_DIR/dist"

ARCH=$(uname -m)
FINAL_NAME="${BINARY_NAME}-${ARCH}.AppImage"

ICON="$(pwd)/assets/icon.png"
DESKTOP="$(pwd)/assets/grassy.desktop"
APPIMAGETOOL="$(pwd)/appimagetool-x86_64.AppImage"

echo "🔨 Building Grassy AppImage (CI-safe)..."

# --- Validate assets ---
[ -f "$ICON" ] || { echo "❌ Missing icon"; exit 1; }
[ -f "$DESKTOP" ] || { echo "❌ Missing desktop file"; exit 1; }

# --- Fetch appimagetool if missing ---
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "⬇️ Downloading appimagetool..."
    wget -q -O "$APPIMAGETOOL" \
        https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x "$APPIMAGETOOL"
fi

# --- Python environment ---
echo "📦 Setting up Python..."
VENV_DIR="$BUILD_DIR/venv"
python3 -m venv "$VENV_DIR" --clear
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r requirements.txt pyinstaller

# --- Force GTK4 awareness ---
export GI_TYPELIB_PATH="/usr/lib/girepository-1.0"

# --- Build with PyInstaller ---
echo "⚙️ Building binary..."
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
    --hidden-import=gi.repository.GLib \
    --hidden-import=requests \
    --hidden-import=appdirs \
    src/main.py

# --- AppDir structure ---
echo "📁 Creating AppDir..."
rm -rf "$APPDIR"

mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/lib"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# Copy binary bundle
cp -r "$DIST_DIR/$BINARY_NAME"/* "$APPDIR/usr/bin/"

# --- Minimal GTK runtime (best-effort) ---
echo "📚 Copying runtime libs..."
cp /usr/lib/libgtk-4.so* "$APPDIR/usr/lib/" 2>/dev/null || true
cp /usr/lib/libadwaita-1.so* "$APPDIR/usr/lib/" 2>/dev/null || true
cp /usr/lib/libglib-2.0.so* "$APPDIR/usr/lib/" 2>/dev/null || true
cp /usr/lib/libgobject-2.0.so* "$APPDIR/usr/lib/" 2>/dev/null || true

# --- Desktop + icon ---
cp "$DESKTOP" "$APPDIR/grassy.desktop"
cp "$DESKTOP" "$APPDIR/usr/share/applications/"

cp "$ICON" "$APPDIR/grassy.png"
cp "$ICON" "$APPDIR/.DirIcon"
cp "$ICON" "$APPDIR/usr/share/icons/hicolor/256x256/apps/grassy.png"

# --- AppRun ---
echo "🚀 Creating AppRun..."
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "$0")")"

export PATH="$HERE/usr/bin:$PATH"
export LD_LIBRARY_PATH="$HERE/usr/lib:$LD_LIBRARY_PATH"
export GI_TYPELIB_PATH="$HERE/usr/lib/girepository-1.0:$GI_TYPELIB_PATH"

exec "$HERE/usr/bin/grassy" "$@"
EOF

chmod +x "$APPDIR/AppRun"

# --- Build AppImage (CI-safe: NO FUSE) ---
echo "📀 Building AppImage..."

"$APPIMAGETOOL" \
    --appimage-extract-and-run \
    --comp zstd \
    --mksquashfs-opt "-Xcompression-level 6" \
    --mksquashfs-opt "-b 131072" \
    "$APPDIR" \
    "$FINAL_NAME"

# --- Output ---
mkdir -p "$RELEASE_DIR"

if [ -f "$FINAL_NAME" ]; then
    mv "$FINAL_NAME" "$RELEASE_DIR/"
    echo "✅ Created: $RELEASE_DIR/$FINAL_NAME"
else
    echo "❌ AppImage build failed"
    exit 1
fi

# --- Cleanup ---
echo "🧹 Cleaning..."
rm -rf "$BUILD_DIR" "$APPDIR"

echo "🎉 Done."
