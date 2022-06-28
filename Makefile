
.PHONY: clean
clean: clean-build clean-pyc

.PHONY: clean-build
clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf __pycache__/ .eggs/ .cache/
	rm -rf .tox/ .pytest_cache/ .benchmarks/

.PHONY: clean-pyc
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

.PHONY: lint
lint:
	flake8 exbetapi/
	pylint exbetapi/

.PHONY: test
test:
	poetry run pytest

.PHONY: tox
tox:
	tox

.PHONY: build
build:
	poetry build

.PHONY: install
install: build
	poetry install

.PHONY: install-user
install-user: build
	python3 setup.py install --user

.PHONY: git
git:
	git push --all
	git push --tags

.PHONY: check
check:
	poetry check

.PHONY: docs
docs:
	sphinx-apidoc -d 6 -e -f -o docs exbetapi/
	make -C docs clean html

.PHONY: release
release:
	git diff-index --quiet HEAD || { echo "untracked files! Aborting"; exit 1; }
	git checkout develop
	git checkout -b release/$(shell date +'%Y%m%d')
	git push origin release/$(shell date +'%Y%m%d')
