#!/bin/bash
set -euo pipefail

BINARY_NAME="grassy"
RELEASE_DIR="release"
APPDIR="$RELEASE_DIR/AppDir"
BUILD_DIR="$RELEASE_DIR/build"
DIST_DIR="$RELEASE_DIR/dist"

APPIMAGETOOL="./appimagetool-x86_64.AppImage"

echo "🔨 Minimal AppImage build..."

python -m venv "$BUILD_DIR/venv"
"$BUILD_DIR/venv/bin/pip" install --upgrade pip
"$BUILD_DIR/venv/bin/pip" install pyinstaller -r requirements.txt



cp assets/icon.png "$APPDIR/grassy.png"

"$BUILD_DIR/venv/bin/python" -m PyInstaller \
    --name "$BINARY_NAME" \
    --onedir \
    --windowed \
    --distpath "$DIST_DIR" \
    --workpath "$BUILD_DIR/pyi" \
    --specpath "$BUILD_DIR" \
    src/main.py

rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"

cp -r "$DIST_DIR/$BINARY_NAME/"* "$APPDIR/usr/bin/"

# --- desktop + icon ---
cp assets/grassy.desktop "$APPDIR/"
cp assets/icon.png "$APPDIR/.DirIcon"

# --- AppRun (minimal) ---
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/grassy" "$@"
EOF

chmod +x "$APPDIR/AppRun"

# --- build AppImage ---
chmod +x "$APPIMAGETOOL"

"$APPIMAGETOOL" --appimage-extract-and-run "$APPDIR" "$RELEASE_DIR/grassy-x86_64.AppImage"

echo "✅ Done: release/grassy-x86_64.AppImage"
