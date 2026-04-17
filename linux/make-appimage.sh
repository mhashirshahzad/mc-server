#!/bin/bash
set -euo pipefail

echo "🔨 Building AppImage with compatibility fixes..."

APP_NAME="grassy"
RELEASE_DIR="release"
APPDIR="$RELEASE_DIR/AppDir"  # ← This was missing!

echo "📦 Building binary with make..."
make binary

echo "🎨 Copying assets..."
cp assets/icon.png "$APPDIR/$APP_NAME.png" 2>/dev/null || echo "⚠️  icon.png not found"
cp assets/grassy.desktop "$APPDIR/" 2>/dev/null || echo "⚠️  grassy.desktop not found"

echo "📦 Building final AppImage..."
make appimage

echo "✅ Done! AppImage created in $RELEASE_DIR/"
