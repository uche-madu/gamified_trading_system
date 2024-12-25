# Gamified Trading System

[![CI Pipeline](https://github.com/uche-madu/gamified_trading_system/actions/workflows/ci.yml/badge.svg)](https://github.com/uche-madu/gamified_trading_system/actions/workflows/ci.yml) [![codecov](https://codecov.io/gh/uche-madu/gamified_trading_system/graph/badge.svg?token=RowUEAILCi)](https://codecov.io/gh/uche-madu/gamified_trading_system)

## Overview

The **Gamified Trading System API** is a robust and scalable backend solution designed for managing portfolios, assets, leaderboards, and user accounts in a gamified trading ecosystem. The API facilitates user engagement through virtual trading operations, leaderboard rankings, and portfolio management, empowering businesses to offer an immersive and interactive experience for their users.

To ensure seamless schema evolution, the API leverages **Alembic** for database migration management, enabling efficient and reliable updates to the database structure over time.

The backend is built with **FastAPI** for high-performance API development and **SQLAlchemy** for database interactions. Swagger UI is available for exploring and interacting with the API endpoints.

This project emphasizes modularity, scalability, and maintainability, with comprehensive testing implemented using **pytest**.

---

## About Tests

Comprehensive testing has been implemented to ensure the system's functionality, reliability, and robustness. The tests cover various components and scenarios, including:

1. **Services**:
   - Validates the core business logic to ensure the correct functioning of key operations, such as:
     - Buying and selling assets with accurate updates to user portfolios and balances.
     - Managing portfolios, including asset addition, removal, and quantity adjustments.
     - Applying milestone bonuses to reward users for specific achievements, such as reaching trade thresholds.

2. **Routes**:
   - Ensures that API endpoints behave as expected by:
     - Responding correctly to valid inputs.
     - Handling errors gracefully for invalid or missing data.

3. **Edge Cases**:
   - Tests the system's behavior in critical and uncommon scenarios, such as:
     - Insufficient balance or asset quantity during a trade.
     - Actions involving non-existent or unauthorized resources.
     - Invalid request formats, ensuring the system handles them robustly.

4. **End-to-End (E2E) Tests**:
   - Validates the full workflow of the system, ensuring smooth integration between API endpoints and backend services. The E2E tests simulate a complete user journey, starting with user creation and depositing initial balances. It covers setting up portfolios, adding assets to the system, and performing trades where users buy and sell assets. After trades, the tests verify that portfolio updates are accurate, including adjusted asset quantities and updated user balances. Finally, the leaderboard is tested to ensure rankings are correctly calculated, with ties and rank orders handled properly. These tests ensure the entire system functions cohesively from start to finish.

For detailed instructions on how to run these tests, see the [Running Tests](#running-tests) section below.

![API Endpoints](assets/gamified_trading_fastapi_1.png)

## Functionality

### 1. **Users**

- Users can be created with unique IDs and usernames.
- User information includes attributes such as:
  - `id`: Unique identifier.
  - `username`: User's name.
  - `gem_count`: Number of gems earned through trading milestones.
  - `rank`: User's rank based on their gem count.

### 2. **Assets**

- Assets represent tradeable items (e.g., stocks, commodities).
- Each asset has:
  - `id`: Unique identifier.
  - `name`: Name of the asset (e.g., "Gold", "Silver").
  - `price`: Price of the asset.

#### Supported Operations

- **Create an Asset**: Add new assets to the system.
- **Retrieve an Asset**: Get details of a specific asset.
- **Update an Asset**: Modify asset name or price.
- **Delete an Asset**: Remove an asset from the system.
- **List All Assets**: Retrieve all available assets.

### 3. **Portfolios**

- A portfolio is associated with a user and contains the assets they own.
- **Portfolio Assets** include:
  - `asset_id`: ID of the asset.
  - `name`: Name of the asset.
  - `quantity`: Number of units owned.
  - `price`: Price at the time of adding to the portfolio.

#### Supported Portfolio Operations

- **Create a Portfolio**: Initialize a portfolio for a user.
- **Add Asset to Portfolio**: Buy and add an asset to the user's portfolio.
- **Remove Asset from Portfolio**: Sell an asset from the portfolio.
- **List Portfolio Assets**: Retrieve all assets in the user's portfolio.
- **Calculate Portfolio Value**: Compute the total value of a portfolio based on current asset prices.

#### Response Includes

- A confirmation message detailing:
  - Quantity of the asset traded.
  - Asset name.
  - Price at which the trade was executed.
  - Total value of the transaction.

### 4. **Leaderboard**

- Users are ranked based on their **gem count**, which increases as they trade assets and achieve milestones.
- Ranks are dynamically assigned after every trade operation.

#### Supported Leaderboard Operations

- **Retrieve Leaderboard**: List the top `N` users sorted by their gem count.

---

## Key Features

- **Gamification**: Users earn gems based on trading milestones:
  - 1 gem per trade.
  - Bonus gems for achieving milestones like 5 and 10 trades.
- **User Management**: Create, retrieve, update, and manage user accounts, including virtual balances.
- **Dynamic Rankings**: Leaderboard ranks users in real time based on gem count.
- **Portfolio Management**: Users can view, add, update, and delete assets within their portfolios.
- **Asset Management**: Admins can manage assets by adding, updating, or removing them.
- **Robust Testing**: Comprehensive test suite using `pytest` ensures reliability of services and routes.
- **Database Migration**: Fully integrated database migration using Alembic ensures seamless schema evolution.
- **Scalable Architecture**: Built using FastAPI, SQLAlchemy, and Docker, ensuring modularity and scalability.

---

## API Endpoints

### **Users**

| Method | Endpoint              | Description                                                |
|--------|-----------------------|------------------------------------------------------------|
| GET    | `/users/`             | List all users.                                            |
| POST   | `/users/`             | Create a new user.                                         |
| GET    | `/users/{user_id}`    | Retrieve a user's information.                            |
| POST   | `/users/deposit`      | Deposit an amount into the user's balance.                |
| POST   | `/users/withdraw`     | Withdraw an amount from the user's balance.               |

![Users](assets/gamified_trading_fastapi_users_get_docs.png)

### **Assets**

| Method | Endpoint              | Description                       |
|--------|-----------------------|-----------------------------------|
| POST   | `/assets/`            | Create a new asset.              |
| GET    | `/assets/{asset_id}`  | Retrieve an asset by ID.         |
| PUT    | `/assets/{asset_id}`  | Update asset details.            |
| DELETE | `/assets/{asset_id}`  | Delete an asset.                 |
| GET    | `/assets/`            | List all assets.                 |

![Assets Redoc](assets/gamified_trading_fastapi_assets_redoc.png)

### **Portfolios**

| Method | Endpoint                          | Description                                                |
|--------|-----------------------------------|------------------------------------------------------------|
| POST   | `/portfolios/`                    | Create a portfolio for a user.                             |
| POST   | `/portfolios/{user_id}/assets/`   | Buy and add an asset to the portfolio.                             |
| DELETE | `/portfolios/{user_id}/assets/{asset_id}` | Sell all or part of an asset a the portfolio. |
| GET    | `/portfolios/{user_id}/`          | Retrieve a user's portfolio and its assets.               |
| GET    | `/portfolios/{user_id}/value`     | Calculate the portfolio's total value.                    |
| GET    | `/portfolios/{user_id}/assets/{asset_id}` | Retrieve details of a specific asset in a user's portfolio.|
| GET    | `/portfolios/{user_id}/assets/`   | List all assets in a user's porfolio                      |

![Portfolios Redoc](assets/gamified_trading_fastapi_portfolios_redoc.png)

### **Leaderboard**

| Method | Endpoint              | Description                           |
|--------|-----------------------|---------------------------------------|
| GET    | `/leaderboard/`       | Retrieve the top-ranked users.        |

![Leaderboard Redoc](assets/gamified_trading_fastapi_leaderboard_redoc.png)

---

## Tech Stack

- **Python**: Backend logic and API implementation.
- **FastAPI**: High-performance web framework for building APIs.
- **SQLAlchemy**: ORM for database interactions.
- **Alembic**: Database migration management.
- **PostgreSQL**: Relational database for persistent storage.
- **Pytest**: Testing framework for ensuring code quality.
- **Docker**: Containerization for isolated development and deployment.
- **Make**: Simplifies running tasks like testing and deployment.

---

## How to Run the Project

The project uses a **Makefile** to simplify setup, running, and testing tasks. Docker is the preferred environment for running the project, including database migrations and tests.

### **1. Local Setup (Development Environment)**

To run the project locally on your machine:

#### Prerequisites

- Python 3.12+
- PostgreSQL installed locally
- Virtual Environment (`venv`)
- `make` installed
- Docker and Docker Compose installed (preferred for running tests and the project). The integration and e2e tests require a postgres database just like the main application. Therefore, running the docker-backed `make` commands simplifies things.

#### Steps

1. **Clone the Repository**:

    ```bash
    git clone git@github.com:uche-madu/gamified_trading_system.git
    cd gamified_trading_system
    ```

2. **Install Dependencies**:
   Use the `install` target to set up a virtual environment and install dependencies:

    ```bash
    make install
    ```

3. **Apply Migrations**:

    ```bash
    alembic upgrade head
    ```

4. **Run the Application Locally**:
    Start the application:

    ```bash
    make run-local
    ```

    Access the API documentation at: <http://localhost:8002/docs>.

### **2. Run Using Docker Compose (The Preferred Way)**

To run the project with Docker Compose, follow these steps:

**Prerequisites**:

- Docker
- Docker Compose

**Steps**:

1. **Clone the Repository**:

    ```bash
    git clone git@github.com:uche-madu/gamified_trading_system.git
    cd gamified_trading_system
    ```

2. **Start the Services**:
   Use the `docker-up` target to start all services:

    ```bash
    make docker-up
    ```

3. **Apply Migrations**:

    ```bash
    make alembic-upgrade
    ```

4. **Stop the Services**:
   Use the `docker-down` target to stop the services:

    ```bash
    make docker-down
    ```

5. **Rebuild the Services**:
   If you need to rebuild the services (e.g., after making code changes), use:

    ```bash
    make docker-rebuild
    ```

---

### **3. Database Migrations with Alembic**

To manage database schema changes, use Alembic via the Docker environment:

1. **Create a Migration Script**:

    ```bash
    make alembic-revision message="Migration message"
    ```

2. **Apply Migrations**:

    ```bash
    make alembic-upgrade
    ```

3. **Downgrade Migrations**:

    ```bash
    make alembic-downgrade
    ```

---

## Running Tests

The preferred way to run tests is in the Docker environment to ensure consistency and compatibility.

### **Makefile Targets for Testing**

1. **Run All Tests**:

    ```bash
    make all-tests
    ```

2. **Run Specific Categories of Tests**:
    - Unit Tests:

        ```bash
        make unit-tests
        ```

    - Functional Tests:

        ```bash
        make functional-tests
        ```

    - Integration Tests:

        ```bash
        make integration-tests
        ```

    - End-to-End (E2E) Tests:

        ```bash
        make e2e-tests
        ```

3. **Run Tests with Coverage**:
    - Integration and E2E Tests with Coverage:

        ```bash
        make integration-e2e-tests-with-coverage
        ```

    - All Tests with Coverage:

        ```bash
        make all-tests-with-coverage
        ```

4. **Run Local Tests (Without Docker)**:
    For unit and functional tests using SQLite:

    ```bash
    make test-local
    ```

---

### **Running a Specific Test**

You can run an individual test using `pytest` within the Docker container. For example:

```bash
docker exec -it gamified_trading_fastapi pytest -m integration -k test_list_portfolio_assets -v
```

**Notes**:

- The `pip install -e .` step (executed during `make install`) ensures your project is installed as an editable package and paths resolve.
- Docker Compose streamlines deployment by combining PostgreSQL and the FastAPI backend.

## API Documentation

You can explore the API using the following documentation pages generated by **FastAPI**:

1. **Swagger UI** (Interactive API Documentation):
   - Visit: [http://localhost:8000/docs](http://localhost:8000/docs)

2. **ReDoc** (Alternative API Documentation):
   - Visit: [http://localhost:8000/redoc](http://localhost:8000/redoc)

Both pages allow you to view all available endpoints, input/output schemas, and test the API directly (Swagger UI only).

## Summary of Makefile Commands

| Command                         | Description                                      |
|---------------------------------|--------------------------------------------------|
| `make install`                  | Set up virtual environment and install dependencies. |
| `make run-local`                | Run the application locally with Uvicorn.       |
| `make docker-up`                | Start services using Docker Compose.            |
| `make docker-down`              | Stop Docker Compose services.                   |
| `make docker-rebuild`           | Rebuild Docker Compose services.                |
| `make all-tests`                | Run all tests in Docker.                        |
| `make test-local`               | Run local tests (unit and functional).          |
| `make lint-format`              | Run Ruff, Black, and Yamllint checks.           |
| `make precommit`                | Run pre-commit hooks and fix issues.            |
| `make alembic-revision`         | Create a new Alembic migration script.          |
| `make alembic-upgrade`          | Apply Alembic migrations.                       |
| `make alembic-downgrade`        | Rollback Alembic migrations.                    |
| `make integration-e2e-tests-with-coverage` | Run integration and E2E tests with coverage. |
