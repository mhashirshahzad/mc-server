VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip3
BINARY_NAME = grassy
INSTALL_PATH = /usr/local/bin
DESKTOP_PATH = $(HOME)/.local/share/applications

# Colors - use with echo -e
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
NC = \033[0m

.PHONY: setup run clean install uninstall upgrade check dev-install desktop-file update fix-venv

setup:
	@echo -e "$(YELLOW)Setting up virtual environment...$(NC)"
	@if ! python3 -c "import venv" 2>/dev/null; then \
		echo -e "$(RED)❌ python3-venv is not installed. Please install it:$(NC)"; \
		echo "   Arch: sudo pacman -S python-virtualenv"; \
		echo "   Ubuntu/Debian: sudo apt install python3-venv"; \
		echo "   Fedora: sudo dnf install python3-virtualenv"; \
		exit 1; \
	fi
	python3 -m venv $(VENV)
	@echo -e "$(YELLOW)Installing dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install pygobject requests
	@echo -e "$(YELLOW)Installing LSP...$(NC)"
	$(PIP) install python-lsp-server
	@echo -e "$(GREEN)✅ Setup complete! Run 'make run'$(NC)"

upgrade:
	$(PIP) install --upgrade pygobject pyinstaller

run:
	@echo -e "$(YELLOW)Running...$(NC)"
	@if [ ! -f "$(PYTHON)" ]; then \
		echo -e "$(RED)Virtual environment not found. Running setup...$(NC)"; \
		$(MAKE) setup; \
	fi
	$(PYTHON) src/main.py

install: setup desktop-file
	@echo -e "$(YELLOW)Creating symlink...$(NC)"
	sudo ln -sf $(PWD)/src/main.py $(INSTALL_PATH)/grassy
	sudo chmod +x $(INSTALL_PATH)/grassy
	@echo -e "$(YELLOW)Installing desktop entry...$(NC)"
	mkdir -p $(DESKTOP_PATH)
	cp grassy.desktop $(DESKTOP_PATH)/
	@echo -e "$(GREEN)✅ Installation complete!$(NC)"
	@echo -e "$(RED)⚠️  WARNING: Don't delete this folder!$(NC)"
	@echo -e "$(GREEN)You can now run 'grassy' from anywhere$(NC)"

uninstall:
	@echo -e "$(YELLOW)Removing binary from $(INSTALL_PATH)...$(NC)"
	sudo rm -f $(INSTALL_PATH)/$(BINARY_NAME)
	@echo -e "$(YELLOW)Removing desktop entry...$(NC)"
	rm -f $(DESKTOP_PATH)/grassy.desktop
	@echo -e "$(YELLOW)Cleaning build files...$(NC)"
	rm -rf build dist *.spec
	@echo -e "$(GREEN)✅ Uninstall complete$(NC)"

clean:
	@echo -e "$(YELLOW)Cleaning...$(NC)"
	rm -rf $(VENV)
	rm -rf build dist *.spec
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo -e "$(GREEN)✅ Clean complete$(NC)"

check:
	$(PIP) list

# Create desktop file
desktop-file:
	@echo -e "$(YELLOW)Creating desktop file...$(NC)"
	@echo "[Desktop Entry]" > grassy.desktop
	@echo "Type=Application" >> grassy.desktop
	@echo "Name=Grassy" >> grassy.desktop
	@echo "Comment=Minecraft Server Manager" >> grassy.desktop
	@echo "Exec=$(INSTALL_PATH)/grassy" >> grassy.desktop
	@echo "Icon=grassy" >> grassy.desktop
	@echo "Terminal=false" >> grassy.desktop
	@echo "Categories=Game;System;" >> grassy.desktop
	@echo -e "$(GREEN)✅ Desktop file created$(NC)"

# Development install (just symlink, no desktop entry)
dev-install:
	@echo -e "$(YELLOW)Creating symlink for development...$(NC)"
	sudo ln -sf $(PWD)/src/main.py $(INSTALL_PATH)/grassy
	sudo chmod +x $(INSTALL_PATH)/grassy
	@echo -e "$(GREEN)✅ Development symlink created$(NC)"
	@echo -e "$(RED)⚠️  WARNING: Don't delete this folder!$(NC)"

update:
	git pull
	@echo -e "$(GREEN)✅ Updated! Run 'make install' to reinstall if needed$(NC)"

# Fix for multiple distros
fix-venv:
	@echo -e "$(YELLOW)Detecting distribution...$(NC)"
	@if command -v pacman &> /dev/null; then \
		echo "Arch Linux detected. Installing python-virtualenv..."; \
		sudo pacman -S python-virtualenv; \
	elif command -v dnf &> /dev/null; then \
		echo "Fedora detected. Installing python3-virtualenv..."; \
		sudo dnf install python3-virtualenv; \
	elif command -v apt &> /dev/null; then \
		echo "Debian/Ubuntu detected. Installing python3-venv..."; \
		sudo apt install python3-venv; \
	else \
		echo -e "$(RED)❌ Could not detect package manager. Please install python3-venv manually$(NC)"; \
		exit 1; \
	fi
	@echo -e "$(GREEN)✅ Virtual environment support installed$(NC)"
