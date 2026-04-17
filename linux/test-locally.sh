#!/bin/bash
# Simulates GitHub Actions Ubuntu runner environment

# Set GitHub Actions environment variables
export GITHUB_ACTIONS=true
export GITHUB_REPOSITORY="${GITHUB_REPOSITORY:-yourusername/grassy}"
export GITHUB_WORKSPACE="$(pwd)"

# Use the same Ubuntu version GitHub uses (22.04 or 24.04)
docker run --rm -it \
  -v "$(pwd):/workspace" \
  -w /workspace \
  -e GITHUB_ACTIONS=true \
  -e GITHUB_REPOSITORY="$GITHUB_REPOSITORY" \
  -e GITHUB_WORKSPACE=/workspace \
  ubuntu:22.04 \
  /bin/bash -c "
    # Update and install dependencies
    apt-get update
    apt-get install -y git wget file binutils fuse3 libfuse2 \
                       python3 python3-pip python3-gi \
                       gir1.2-gtk-4.0 libadwaita-1-dev \
                       desktop-file-utils
    
    # Install quick-sharun (or your AppImage tool)
    wget https://github.com/AppImage/AppImageKit/releases/download/continuous/quick-sharun-x86_64.AppImage
    chmod +x quick-sharun-x86_64.AppImage
    ln -s quick-sharun-x86_64.AppImage /usr/local/bin/quick-sharun
    
    # Run your build script
    bash /workspace/linux/make-appimage.sh
    
    # Test the output
    ls -la /workspace/dist/
  "
