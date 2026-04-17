#!/bin/sh
set -eu

ARCH=$(uname -m)
if git describe --tags --always 2>/dev/null; then
    VERSION=$(git describe --tags --always)
else
    VERSION="dev"
fi
export ARCH VERSION
export OUTPATH=./dist
export ADD_HOOKS="self-updater.hook"
export UPINFO="gh-releases-zsync|${GITHUB_REPOSITORY%/*}|${GITHUB_REPOSITORY#*/}|latest|*$ARCH.AppImage.zsync"

# --- Required metadata ---
export ICON="$(pwd)/assets/icon.png"
export DESKTOP="$(pwd)/grassy.desktop"

# --- Deployment options ---
export DEPLOY_PYTHON=1
export DEPLOY_GTK=1
export GTK_DIR=gtk-4.0
export DEPLOY_LOCALE=1
export STARTUPWMCLASS=io.github.yourusername.grassy
export GTK_CLASS_FIX=1

# --- Create basic AppDir first ---
mkdir -p ./AppDir/usr/bin
mkdir -p ./AppDir/usr/share/applications
mkdir -p ./AppDir/usr/share/icons/hicolor/256x256/apps

# Copy your files into AppDir
cp "$ICON" ./AppDir/usr/share/icons/hicolor/256x256/apps/grassy.png
cp "$ICON" ./AppDir/icon.png
cp "$ICON" ./AppDir/.DirIcon
cp "$DESKTOP" ./AppDir/usr/share/applications/
cp "$DESKTOP" ./AppDir/grassy.desktop

# Copy your Python script (THIS is what quick-sharun will bundle)
cp ./grassy.py ./AppDir/usr/bin/grassy
chmod +x ./AppDir/usr/bin/grassy

# --- NOW run quick-sharun on the AppDir contents ---
# Point it to the python3 binary and your script (both exist in runner)
quick-sharun /usr/bin/python3 \
             /usr/lib/python3.*/site-packages/gi \
             /usr/lib/python3.*/site-packages/requests \
             /usr/lib/python3.*/site-packages/appdirs \
             /usr/lib/x86_64-linux-gnu/libgobject* \
             /usr/lib/x86_64-linux-gnu/libglib* \
             /usr/lib/x86_64-linux-gnu/libgtk* \
             /usr/lib/x86_64-linux-gnu/libadwaita* \
             /usr/lib/x86_64-linux-gnu/girepository-1.0 \
             /usr/lib/python3/dist-packages/gi \
             ./AppDir/usr/bin/grassy

# --- Create AppRun wrapper that uses bundled python ---
cat > ./AppDir/AppRun << 'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
export PATH="${HERE}/usr/bin:${PATH}"
export PYTHONPATH="${HERE}/usr/lib/python3/dist-packages:${HERE}/usr/lib/python3.12/site-packages:${PYTHONPATH:-}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH:-}"
export GI_TYPELIB_PATH="${HERE}/usr/lib/girepository-1.0:${GI_TYPELIB_PATH:-}"
exec "${HERE}/usr/bin/python3" "${HERE}/usr/bin/grassy" "$@"
EOF
chmod +x ./AppDir/AppRun

# --- Build the AppImage ---
quick-sharun --make-appimage

# --- Test it ---
quick-sharun --test ./dist/*.AppImage
