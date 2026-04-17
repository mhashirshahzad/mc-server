VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip3
BINARY_NAME = grassy
RELEASE_DIR = release
DIST_DIR = $(RELEASE_DIR)/dist
BUILD_DIR = $(RELEASE_DIR)/build
APPDIR = $(RELEASE_DIR)/Grassy.AppDir
APPIMAGE_TOOL = ./appimagetool-x86_64.AppImage
INSTALL_PATH = /usr/local/bin
DESKTOP_PATH = $(HOME)/.local/share/applications

# Read version from version.txt
ifneq ($(wildcard version.txt),)
    BINARY_VERSION := $(shell cat version.txt | tr -d '\n\r')
else
    $(error version.txt not found. Please create it with your version number)
endif

# Colors
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
NC = \033[0m

.PHONY: version setup run clean install uninstall upgrade check dev-install desktop-file update fix-venv binary appimage release

version:
	@echo "$(BINARY_VERSION)"

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

binary:
	@echo -e "$(YELLOW)Building release binary v$(BINARY_VERSION)...$(NC)"
	@if [ ! -f "$(PYTHON)" ]; then $(MAKE) setup; fi
	$(PIP) install pyinstaller
	$(PIP) install -r requirements.txt
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

appimage:
	@echo -e "$(YELLOW)Creating AppImage for v$(BINARY_VERSION)...$(NC)"
	
	@if [ ! -d "$(DIST_DIR)/$(BINARY_NAME)" ]; then \
		echo -e "$(RED)❌ Release not found. Run 'make binary' first$(NC)"; \
		exit 1; \
	fi
	
	rm -rf $(APPDIR)
	mkdir -p $(APPDIR)/usr/bin
	
	cp -r $(DIST_DIR)/$(BINARY_NAME)/* $(APPDIR)/usr/bin/
	
	printf '%s\n' \
'#!/bin/bash' \
'HERE="$$(dirname "$$(readlink -f "$$0")")"' \
'export GI_TYPELIB_PATH="$$HERE/usr/bin/lib/girepository-1.0"' \
'export GTK_DATA_PREFIX="$$HERE/usr/bin"' \
'export XDG_DATA_DIRS="$$HERE/usr/bin/share:$$XDG_DATA_DIRS"' \
'exec "$$HERE/usr/bin/grassy" "$$@"' \
> $(APPDIR)/AppRun
	
	chmod +x $(APPDIR)/AppRun
	
	@if [ -f grassy.desktop ]; then cp grassy.desktop $(APPDIR)/; \
	else echo -e "$(YELLOW)⚠ grassy.desktop not found$(NC)"; fi
	
	@if [ -f assets/icon.png ]; then cp assets/icon.png $(APPDIR)/grassy.png; \
	else echo -e "$(YELLOW)⚠ assets/icon.png not found$(NC)"; fi
	
	chmod +x $(APPIMAGE_TOOL) 2>/dev/null || true
	
	@if [ -f $(APPIMAGE_TOOL) ]; then \
		$(APPIMAGE_TOOL) $(APPDIR) $(RELEASE_DIR)/$(BINARY_NAME)-$(BINARY_VERSION)-x86_64.AppImage; \
		echo -e "$(GREEN)✅ AppImage created: $(RELEASE_DIR)/$(BINARY_NAME)-$(BINARY_VERSION)-x86_64.AppImage$(NC)"; \
	else \
		echo -e "$(RED)❌ $(APPIMAGE_TOOL) not found. Download from https://github.com/AppImage/AppImageKit/releases$(NC)"; \
		exit 1; \
	fi

release: binary appimage
	@echo -e "$(GREEN)✅ Full release v$(BINARY_VERSION) complete!$(NC)"
	@echo -e "$(YELLOW)Files created:$(NC)"
	@ls -lh $(RELEASE_DIR)/*$(BINARY_VERSION)* 2>/dev/null || echo "  No versioned files found"

clean:
	@echo -e "$(YELLOW)Cleaning...$(NC)"
	rm -rf $(VENV) $(RELEASE_DIR) build/ dist/ *.spec
	@echo -e "$(GREEN)✅ Clean complete$(NC)"

install:
	@echo -e "$(YELLOW)Installing to $(INSTALL_PATH)...$(NC)"
	@if [ ! -f "$(DIST_DIR)/$(BINARY_NAME)/$(BINARY_NAME)" ]; then \
		echo -e "$(RED)❌ Binary not found. Run 'make binary' first$(NC)"; \
		exit 1; \
	fi
	sudo cp -r $(DIST_DIR)/$(BINARY_NAME)/* $(INSTALL_PATH)/
	sudo chmod +x $(INSTALL_PATH)/$(BINARY_NAME)
	@echo -e "$(GREEN)✅ Installed to $(INSTALL_PATH)$(NC)"

uninstall:
	@echo -e "$(YELLOW)Uninstalling...$(NC)"
	sudo rm -f $(INSTALL_PATH)/$(BINARY_NAME)
	sudo rm -rf $(INSTALL_PATH)/$(BINARY_NAME)_*
	@echo -e "$(GREEN)✅ Uninstalled$(NC)"

upgrade:
	@echo -e "$(YELLOW)Upgrading dependencies...$(NC)"
	$(PIP) install --upgrade -r requirements.txt
	@echo -e "$(GREEN)✅ Upgrade complete$(NC)"

check:
	@echo -e "$(YELLOW)Checking environment...$(NC)"
	@echo "Python: $$(python3 --version 2>&1)"
	@echo "Version from file: $(BINARY_VERSION)"
	@echo "Binary name: $(BINARY_NAME)"
	@if [ -f requirements.txt ]; then echo "✅ requirements.txt found"; else echo "❌ requirements.txt missing"; fi
	@if [ -f src/main.py ]; then echo "✅ src/main.py found"; else echo "❌ src/main.py missing"; fi
	@echo -e "$(GREEN)✅ Check complete$(NC)"

dev-install:
	@echo -e "$(YELLOW)Installing in development mode...$(NC)"
	$(PIP) install -e .
	@echo -e "$(GREEN)✅ Dev install complete$(NC)"

desktop-file:
	@echo -e "$(YELLOW)Installing desktop file...$(NC)"
	@if [ ! -f grassy.desktop ]; then \
		echo -e "$(RED)❌ grassy.desktop not found$(NC)"; \
		exit 1; \
	fi
	mkdir -p $(DESKTOP_PATH)
	cp grassy.desktop $(DESKTOP_PATH)/
	update-desktop-database $(DESKTOP_PATH) 2>/dev/null || true
	@echo -e "$(GREEN)✅ Desktop file installed$(NC)"

update: upgrade

fix-venv:
	@echo -e "$(YELLOW)Fixing virtual environment...$(NC)"
	rm -rf $(VENV)
	$(MAKE) setup
	@echo -e "$(GREEN)✅ Virtual environment rebuilt$(NC)"

help:
	@echo -e "$(YELLOW)Available commands:$(NC)"
	@echo "  make setup         - Create venv and install dependencies"
	@echo "  make run           - Run the application"
	@echo "  make binary        - Build PyInstaller binary"
	@echo "  make appimage      - Create AppImage from binary"
	@echo "  make release       - Build both binary and AppImage"
	@echo "  make clean         - Remove venv and build artifacts"
	@echo "  make install       - Install to /usr/local/bin"
	@echo "  make uninstall     - Remove from /usr/local/bin"
	@echo "  make upgrade       - Upgrade dependencies"
	@echo "  make check         - Check environment and files"
	@echo "  make version       - Show current version"
	@echo "  make help          - Show this help"

.DEFAULT_GOAL := help
