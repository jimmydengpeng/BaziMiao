PYTHON ?= python
PIP ?= pip
WEB_DIR ?= src/web

.PHONY: setup dev test lint fmt web-setup web-dev web-build

setup:
	$(PIP) install -r requirements.txt

dev:
	@if [ -f .env ]; then uvicorn src.api.server:app --reload --port 8000 --env-file .env; else uvicorn src.api.server:app --reload --port 8000; fi

web-setup:
	cd $(WEB_DIR) && npm install

web-dev:
	cd $(WEB_DIR) && npm run dev -- --host

web-build:
	cd $(WEB_DIR) && npm run build

test:
	pytest

lint:
	ruff src

fmt:
	black src
