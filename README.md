# Cash Register

Python cash register implementation with strict typing and testing.

## Setup

```bash
# Install dependencies
poetry install

# Install pre-commit hooks
pre-commit install
```

## Quality Checks

```bash
# Run tests with coverage
poetry run pytest --cov

# Type checking
poetry run mypy src/

# Run linters
pre-commit run --all-files
```

## Makefile Commands

```bash
# Run all quality checks (mypy + pre-commit)
make check

# Run complete CI pipeline (lint → mypy → tests + coverage)
make check-all

# Run tests
make test

# Run tests with coverage report
make coverage

# Run tests with coverage (fails if < 80%)
make coverage-check

# Run type checking
make mypy

# Run pre-commit hooks
make precommit

# Increment version patch
make version-patch
```

## Requirements

- Test coverage ≥ 80%
- Strict typing (mypy)
- Code formatting (black/isort)
- Style checking (flake8)
- CI pipeline validating all checks 