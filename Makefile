TESTS_DIR := PaladinEngine/tests/unit_tests
ROOT := $(shell pwd)
ROOT_PYTHON_DIR := $(ROOT)/PaladinEngine
all: build-ui

build-ui:
	cd PaladinUI/paladin_server && npm i && npm run build

.PHONY: all build-%

test:
	cd $(TESTS_DIR) && PYTHONPATH=$(ROOT_PYTHON_DIR) pytest

