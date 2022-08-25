all: build-ui

build-ui:
	cd PaladinUI/paladin_server && npm i && npm run build

.PHONY: all build-%
