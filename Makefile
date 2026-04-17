VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip3

BINARY_NAME = grassy
BINARY_VERSION := $(shell cat version.txt 2>/dev/null | tr -d '\n\r')

RELEASE_DIR = release
DIST_DIR = $(RELEASE_DIR)/dist
BUILD_DIR = $(RELEASE_DIR)/build
APPDIR = $(RELEASE_DIR)/Grassy.AppDir

APPIMAGE_TOOL = ./appimagetool-x86_64.AppImage

INSTALL_PATH = /usr/local/bin
DESKTOP_PATH = $(HOME)/.local/share/applications

RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
NC = \033[0m

.PHONY: setup run binary appimage release clean install uninstall upgrade check dev-install desktop-file fix-venv help version

version:
	@echo "$(BINARY_VERSION)"

setup:
	@echo -e "$(YELLOW)Setting up venv...$(NC)"
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo -e "$(GREEN)OK$(NC)"

run:
	@if [ ! -f "$(PYTHON)" ]; then $(MAKE) setup; fi
	$(PYTHON) src/main.py

binary:
	@echo -e "$(YELLOW)Building binary...$(NC)"
	@if [ ! -f "$(PYTHON)" ]; then $(MAKE) setup; fi
	$(PIP) install pyinstaller

	rm -rf $(RELEASE_DIR)

	$(PYTHON) -m PyInstaller \
		--name $(BINARY_NAME) \
		--onedir \
		--windowed \
		--clean \
		--noconfirm \
		--distpath $(DIST_DIR) \
		--workpath $(BUILD_DIR) \
		--specpath $(RELEASE_DIR) \
		--hidden-import=gi \
		--hidden-import=gi.repository \
		--hidden-import=gi.repository.Gtk \
		--hidden-import=gi.repository.Adw \
		--hidden-import=gi.repository.GLib \
		--collect-all=gi \
		src/main.py
		
	@echo -e "$(GREEN)Binary ready$(NC)"

appimage:
	@echo -e "$(YELLOW)Building AppImage...$(NC)"

	@if [ ! -d "$(DIST_DIR)/$(BINARY_NAME)" ]; then \
		echo "Build binary first"; \
		exit 1; \
	fi

	rm -rf $(APPDIR)
	mkdir -p $(APPDIR)/usr/bin

	cp -r $(DIST_DIR)/$(BINARY_NAME)/* $(APPDIR)/usr/bin/

	# AppRun (FIXED GI ENV)
	printf '%s\n' \
'#!/bin/bash' \
'HERE="$$(dirname "$$(readlink -f "$$0")")"' \
'' \
'export GI_TYPELIB_PATH=/usr/lib/girepository-1.0:/usr/lib/x86_64-linux-gnu/girepository-1.0' \
'export LD_LIBRARY_PATH=/usr/lib:/usr/lib/x86_64-linux-gnu:$${LD_LIBRARY_PATH}' \
'export XDG_DATA_DIRS=/usr/share:/usr/local/share:$${XDG_DATA_DIRS}' \
'' \
'exec "$$HERE/usr/bin/grassy" "$$@"' \
> $(APPDIR)/AppRun

	chmod +x $(APPDIR)/AppRun

	# desktop + icon
	@[ -f assets/grassy.desktop ] && cp assets/grassy.desktop $(APPDIR)/ || true
	@[ -f assets/icon.png ] && cp assets/icon.png $(APPDIR)/grassy.png || true

	chmod +x $(APPIMAGE_TOOL) 2>/dev/null || true

	@if [ -f $(APPIMAGE_TOOL) ]; then \
		$(APPIMAGE_TOOL) $(APPDIR) $(RELEASE_DIR)/$(BINARY_NAME)-$(BINARY_VERSION)-x86_64.AppImage; \
		echo "OK AppImage built"; \
	else \
		echo "Missing appimagetool"; \
		exit 1; \
	fi

release: binary appimage
	@echo -e "$(GREEN)Release complete$(NC)"

install:
	@if [ ! -f "$(DIST_DIR)/$(BINARY_NAME)/$(BINARY_NAME)" ]; then \
		echo "Build first"; exit 1; \
	fi
	sudo cp -r $(DIST_DIR)/$(BINARY_NAME)/* $(INSTALL_PATH)/
	sudo chmod +x $(INSTALL_PATH)/$(BINARY_NAME)

uninstall:
	sudo rm -f $(INSTALL_PATH)/$(BINARY_NAME)

clean:
	rm -rf $(VENV) $(RELEASE_DIR) build dist *.spec

check:
	@echo "Python: $$(python3 --version)"
	@echo "Version: $(BINARY_VERSION)"
	@test -f src/main.py && echo OK src/main.py || echo MISSING src/main.py
	@test -f requirements.txt && echo OK requirements.txt || echo MISSING requirements.txt

help:
	@echo "make setup"
	@echo "make run"
	@echo "make binary"
	@echo "make appimage"
	@echo "make release"
	@echo "make clean"
	@echo "make install"
