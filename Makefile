VENV=.venv

all: install

install:
	python3 -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt

init-db:
	cd app/db && ../../$(VENV)/bin/python3 schema.py

test:
	cd tests && ../$(VENV)/bin/pytest

.PHONY: all init-db install test
