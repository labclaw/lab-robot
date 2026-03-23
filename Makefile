.PHONY: dev-install test lint format

dev-install:
	pip install -e ".[dev,opentrons]"

test:
	pytest --cov=lab_robot --cov=robots --cov-report=term-missing --cov-fail-under=100 -q

lint:
	ruff check .
	mypy src/lab_robot/

format:
	ruff check --fix .
	ruff format .
