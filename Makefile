VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip3
BINARY_NAME = grassy
BINARY_VERSION = 1.1.0
RELEASE_DIR = release
DIST_DIR = $(RELEASE_DIR)/dist
BUILD_DIR = $(RELEASE_DIR)/build
APPDIR = $(RELEASE_DIR)/Grassy.AppDir
APPIMAGE_TOOL = ./appimagetool-x86_64.AppImage
INSTALL_PATH = /usr/local/bin
DESKTOP_PATH = $(HOME)/.local/share/applications
# Colors
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
NC = \033[0m
.PHONY: version setup run clean install uninstall upgrade check dev-install desktop-file update fix-venv release-linux appimage
version:
	@echo $(BINARY_VERSION)
setup:
	@echo -e "$(YELLOW)Setting up virtual environment...$(NC)"
	@if ! python3 -c "import venv" 2>/dev/null; then \
		echo -e "$(RED)❌ python3-venv missing$(NC)"; \
		exit 1; \
	fi
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo -e "$(GREEN)✅ Setup complete$(NC)"
run:
	@echo -e "$(YELLOW)Running...$(NC)"
	@if [ ! -f "$(PYTHON)" ]; then $(MAKE) setup; fi
	$(PYTHON) src/main.py
release-linux:
	@echo -e "$(YELLOW)Building release binary...$(NC)"
	@if [ ! -f "$(PYTHON)" ]; then $(MAKE) setup; fi
	$(PIP) install pyinstaller -r requirements.txt
	rm -rf $(RELEASE_DIR)
	$(PYTHON) -m PyInstaller \
		--name $(BINARY_NAME) \
		--onedir \
		--windowed \
		--distpath $(DIST_DIR) \
		--workpath $(BUILD_DIR) \
		--specpath $(RELEASE_DIR) \
		--hidden-import=gi \
		--hidden-import=gi.repository.Gtk \
		--hidden-import=gi.repository.Adw \
		src/main.py
	@echo -e "$(GREEN)✅ Release built in $(RELEASE_DIR)$(NC)"
	make appimage
appimage:
	@echo -e "$(YELLOW)Creating AppImage...$(NC)"
	
	@if [ ! -d "$(DIST_DIR)/$(BINARY_NAME)" ]; then \
		echo -e "$(RED)❌ Release not found. Run 'make release-linux' first$(NC)"; \
		exit 1; \
	fi
	
	rm -rf $(APPDIR)
	mkdir -p $(APPDIR)/usr/bin
	
	cp -r $(DIST_DIR)/$(BINARY_NAME)/* $(APPDIR)/usr/bin/
	
	printf '%s\n' \
'#!/bin/bash' \
'HERE="$$(dirname "$$(readlink -f "$$0")")"' \
'exec "$$HERE/usr/bin/grassy" "$$@"' \
> $(APPDIR)/AppRun
	
	chmod +x $(APPDIR)/AppRun
	
	@if [ -f grassy.desktop ]; then cp grassy.desktop $(APPDIR)/; fi
	@if [ -f assets/icon.png ]; then cp assets/icon.png $(APPDIR)/grassy.png; fi
	
	chmod +x $(APPIMAGE_TOOL)
	
	$(APPIMAGE_TOOL) $(APPDIR) $(RELEASE_DIR)/$(BINARY_NAME)-$(BINARY_VERSION)-x86_64.AppImage
	
	@echo -e "$(GREEN)✅ AppImage created: $(RELEASE_DIR)/$(BINARY_NAME)-$(BINARY_VERSION)-x86_64.AppImage$(NC)"
