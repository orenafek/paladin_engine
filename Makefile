TESTS_DIR := PaladinEngine/tests/unit_tests
ROOT := $(shell pwd)
ROOT_PYTHON_DIR := $(ROOT)/PaladinEngine
all: build-ui

build-ui:
	cd PaladinUI/paladin_server && npm i && npm run build

.PHONY: all build-%

test:
	cd $(TESTS_DIR) && find . -name 'test*.py' -exec sh -c "PYTHONPATH=$(ROOT_PYTHON_DIR) PYTHONDONTWRITEBYTECODE=1 $(ROOT)/.venv/bin/pytest -p no:cacheprovider {}" ";"

