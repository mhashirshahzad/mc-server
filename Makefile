VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

.PHONY: setup run clean install

setup:
	@echo "Setting up virtual environment..."
	python3 -m venv $(VENV)
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install pygobject
	@echo "✅ Setup complete! Run 'make run'"

install:
	$(PIP) install --upgrade pygobject

run:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup..."; \
		$(MAKE) setup; \
	fi
	$(PYTHON) src/main.py

# Clean everything
clean:
	rm -rf $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Check installed packages
check:
	$(PIP) list
