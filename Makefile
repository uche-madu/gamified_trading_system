.PHONY: precommit lint fix install docker-up docker-down docker-rebuild run-local test

VENV=./.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
PYTEST=$(VENV)/bin/pytest

# Run pre-commit, fix issues, and stage files
precommit:
	@echo "Running pre-commit hooks, fixing issues, and staging files..."
	pre-commit run --all-files || true
	@echo "Staging fixed files..."
	git add .
	@echo "Files fixed and staged successfully. Ready for commit!"

# Alias for precommit
fix: precommit

# Run pre-commit lint checks only, without staging files
lint:
	@echo "Running pre-commit lint checks only..."
	pre-commit run --all-files --show-diff-on-failure

# Install project dependencies locally
install:
	@echo "Creating virtual environment and installing dependencies..."
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e .
	@echo "Dependencies installed successfully!"

# Run the project locally using Uvicorn
run-local:
	@echo "Starting the FastAPI application locally..."
	. .venv/bin/activate && uvicorn app.main:app --reload --port 8002

# Docker Compose: Start services
docker-up:
	@echo "Starting services using Docker Compose..."
	docker compose up -d --build

# Docker Compose: Stop services
docker-down:
	@echo "Stopping services..."
	docker compose down

# Docker Compose: Rebuild services
docker-rebuild:
	@echo "Rebuilding services..."
	docker compose down
	docker compose up -d --build

# Run tests
test:
	@echo "Running tests with pytest..."
	$(PYTEST) app/tests --disable-warnings
