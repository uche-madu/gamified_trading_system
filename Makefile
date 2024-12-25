.PHONY: precommit lint fix install docker-up docker-down docker-rebuild run-local test-local unit-tests functional-tests integration-tests e2e-tests all-tests integration-e2e-tests-with-coverage all-tests-with-coverage lint-format


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

# Run Ruff and Yamllint linting and Black formatting checks
lint-format:
	@echo "Running Ruff linting checks..." && \
	ruff check . --fix && \
    echo "Running Black formatting checks..." && \
	black --check .
	echo "Running Yamllint linting checks..." && \
	yamllint .

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

# Run non-docker tests with pytest
test-local:
	@echo "Running tests with pytest..."
	$(PYTEST) app/tests -m "unit or functional"

# Run unit tests in docker container
unit-tests:
	@echo "Running unit tests with pytest..."
	docker exec gamified_trading_fastapi pytest -m unit

# Run functional tests in docker container
functional-tests:
	@echo "Running functional tests with pytest..."
	docker exec gamified_trading_fastapi pytest -m functional

# Run integration tests in docker container
integration-tests:
	@echo "Running integration tests with pytest..."
	docker exec gamified_trading_fastapi pytest -m integration

# Run end-to-end tests in docker container
e2e-tests:
	@echo "Running end-to-end tests with pytest..."
	docker exec gamified_trading_fastapi pytest -m e2e

# Run all tests in docker container
all-tests:
	@echo "Running all tests with pytest..."
	docker exec gamified_trading_fastapi pytest

# Run integration and end-to-end tests in docker container with code coverage
integration-e2e-tests-with-coverage:
	@echo "Running integration and end-to-end tests with pytest and code coverage..."
	docker exec gamified_trading_fastapi pytest --disable-warnings --cov=app --cov-report=xml -m "integration or e2e"

# Run all tests in docker container with code coverage
all-tests-with-coverage:
	@echo "Running all tests with pytest and code coverage..."
	docker exec gamified_trading_fastapi pytest --disable-warnings --cov=app --cov-report=xml

# Alembic: Create a migration revision
alembic-revision:
	@echo "Creating Alembic migration revision..."
	docker exec gamified_trading_fastapi alembic revision --autogenerate -m "$(message)"

# Alembic: Apply migrations
alembic-upgrade:
	@echo "Applying Alembic migrations..."
	docker exec gamified_trading_fastapi alembic upgrade head

# Alembic: Rollback migrations
alembic-downgrade:
	@echo "Rolling back Alembic migrations..."
	docker exec gamified_trading_fastapi alembic downgrade -1
