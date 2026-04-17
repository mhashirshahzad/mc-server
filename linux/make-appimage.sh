#!/bin/bash
set -euo pipefail

# --- configuration ---
binary_name="grassy"
release_dir="release"
appdir="$release_dir/grassy.appdir"
build_dir="$release_dir/build"
dist_dir="$release_dir/dist"

arch=$(uname -m)
final_name="${binary_name}-${arch}.appimage"

icon="$(pwd)/assets/icon.png"
desktop="$(pwd)/assets/grassy.desktop"
appimagetool="$(pwd)/appimagetool-x86_64.appimage"

echo "🔨 building grassy appimage (gtk system-runtime mode)..."

# --- validate assets ---
[ -f "$icon" ] || { echo "❌ missing icon"; exit 1; }
[ -f "$desktop" ] || { echo "❌ missing desktop file"; exit 1; }

# --- fetch appimagetool ---
if [ ! -f "$appimagetool" ]; then
    echo "⬇️ downloading appimagetool..."
    wget -q -o "$appimagetool" \
        https://github.com/appimage/appimagekit/releases/download/continuous/appimagetool-x86_64.appimage
    chmod +x "$appimagetool"
fi

# --- python environment ---
echo "📦 setting up python..."
venv_dir="$build_dir/venv"
python3 -m venv "$venv_dir" --clear
"$venv_dir/bin/pip" install --upgrade pip

# important: do not install pygobject via pip
"$venv_dir/bin/pip" install -r requirements.txt pyinstaller

# --- build with pyinstaller ---
echo "⚙️ building binary..."
"$venv_dir/bin/python" -m pyinstaller \
    --name "$binary_name" \
    --onedir \
    --windowed \
    --distpath "$dist_dir" \
    --workpath "$build_dir/pyinstaller" \
    --specpath "$build_dir" \
    --hidden-import=gi \
    --hidden-import=gi.repository.gtk \
    --hidden-import=gi.repository.adw \
    --hidden-import=gi.repository.glib \
    --hidden-import=requests \
    --hidden-import=appdirs \
    src/main.py

# --- appdir structure ---
echo "📁 creating appdir..."
rm -rf "$appdir"

mkdir -p "$appdir/usr/bin"
mkdir -p "$appdir/usr/share/applications"
mkdir -p "$appdir/usr/share/icons/hicolor/256x256/apps"

# copy pyinstaller bundle
cp -r "$dist_dir/$binary_name"/* "$appdir/usr/bin/"

# --- desktop + icon ---
cp "$desktop" "$appdir/grassy.desktop"
cp "$desktop" "$appdir/usr/share/applications/"

cp "$icon" "$appdir/grassy.png"
cp "$icon" "$appdir/.diricon"
cp "$icon" "$appdir/usr/share/icons/hicolor/256x256/apps/grassy.png"

# --- apprun ---
echo "🚀 creating apprun..."
cat > "$appdir/apprun" << 'eof'
#!/bin/bash
here="$(dirname "$(readlink -f "$0")")"

export path="$here/usr/bin:$path"

exec "$here/usr/bin/grassy" "$@"
eof

chmod +x "$appdir/apprun"

# --- build appimage (no fuse required) ---
echo "📀 building appimage..."
"$appimagetool" \
    --appimage-extract-and-run \
    "$appdir" \
    "$final_name"

# --- output ---
mkdir -p "$release_dir"

if [ -f "$final_name" ]; then
    mv "$final_name" "$release_dir/"
    echo "✅ created: $release_dir/$final_name"
else
    echo "❌ appimage build failed"
    exit 1
fi

# --- cleanup ---
echo "🧹 cleaning..."
rm -rf "$build_dir" "$appdir"

echo "🎉 done."
