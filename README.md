# Application Management System

A simple configuration management service implemented in Python.

## Project Overview

This project provides an interactive CLI for managing application configuration data across environments. It uses an in-memory repository design, which makes it easy to adapt later to a real database.

### Core features

- Onboard a new environment.
- Onboard a new service in an environment.
- Create configuration for a service in a specific environment.
- Update configuration atomically.
- Retrieve configuration for a service in an environment.
- List all environments and their services.

### Configuration data model

Each configuration entry stores:

- `service_name` (e.g. `payment-service`)
- `environment` (e.g. `dev`, `staging`, `production`)
- `data` (flat JSON object with key-value pairs only)
- `created_at` timestamp
- `updated_at` timestamp

### Design notes

- `src/` contains the implementation:
  - `src/cli.py` — Typer-based interactive CLI entrypoint
  - `src/controller.py` — business logic and validation layer
  - `src/repository.py` — in-memory persistence layer and repository interface
  - `src/models.py` — configuration model with validation

- `tests/` contains pytest tests and a results summary file.

## Running the application

From the repository root:

```bash
cd /workspaces/application-management-system
python -m src.cli add-environment staging
python -m src.cli add-service payment-service staging
python -m src.cli set-config payment-service staging timeout_seconds 30
python -m src.cli update-config payment-service staging '{"timeout_seconds": 60, "retry_attempts": 3, "enable_logging": true, "max_connections": 100}'
python -m src.cli get-config payment-service staging
python -m src.cli list-services
```

> Note: The CLI is executed with `python -m src.cli` because the project uses package-relative imports.

## Tests

Run all tests from the repository root:

```bash
cd /workspaces/application-management-system
python -m pytest -q tests
```

For verbose output:

```bash
python -m pytest -vv tests
```

## Additional notes

- The tests are stored in `tests/`.
- `tests/results.txt` contains the test summary and example command output.
- This implementation focuses on simplicity and extensibility: the repository interface can be replaced with a database-backed implementation without changing the CLI or controller.
