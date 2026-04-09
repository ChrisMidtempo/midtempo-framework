.PHONY: help setup install clean

help:
	@echo "Midtempo Framework - Minimal Setup Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup      - Create virtual environment and install all dependencies"
	@echo "  make install    - Install Python and Node dependencies (venv must exist)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean      - Remove generated files and caches"
	@echo ""
	@echo "For development commands, use npm scripts:"
	@echo "  npm run         - List all available npm scripts"

setup:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	npm install
	@echo ""
	@echo "Setup complete! Activate the virtual environment with:"
	@echo "  source venv/bin/activate"
	@echo ""
	@echo "Run 'npm run' to see available development commands"

install:
	pip install -r requirements.txt
	npm install

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
