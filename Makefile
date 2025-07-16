# Makefile for managing the cash_register project
# virtual targets: 
# make test ⟶ poetry run pytest ⟶ exceution in venv of Poetry

.PHONY: test coverage coverage-check mypy check version-patch precommit

# Run tests using pytest

test:
	poetry run pytest

# Check test coverage

coverage:
	poetry run pytest --cov=src

# Run tests with coverage and fail if < 80%

coverage-check:
	poetry run pytest --cov=src --cov-fail-under=80

# Run tests with coverage and fail if < 80%

coverage-ci:
	poetry run pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Run mypy for static type checking

mypy:
	poetry run mypy src/

# Run all checks (mypy + precommit)

check: mypy precommit

# Run full CI pipeline: lint → mypy → tests + coverage

check-all: precommit mypy coverage-ci

# Increment version using SemVer (patch)

version-patch:
	poetry version patch

# Run pre-commit on all files

precommit:
	poetry run pre-commit run --all-files