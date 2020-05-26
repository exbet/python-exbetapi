.PHONY: clean-pyc clean-build docs

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	rm -fr __pycache__/ .eggs/ .cache/ .tox/ .pytest_cache/ .scannerwork/

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	flake8 exbetapi/
	pylint exbetapi/

test:
	poetry run pytest

build:
	poetry build

install: build
	poetry install

git:
	git push --all
	git push --tags

check:
	poetry check

upload:
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

docs:
	sphinx-apidoc -d 6 -e -f -o docs exbetapi/
	make -C docs clean html

docs_store:
	git add docs
	-git commit -m "Updating docs/"

semver: semver-release semver-updates

semver-release:
	-semversioner release

semver-updates:
	semversioner changelog > CHANGELOG.md
	$(eval CURRENT_VERSION = $(shell semversioner current-version))
	sed -i "s/^__version__.*/__version__ = \"$(CURRENT_VERSION)\"/" exbetapi/__init__.py
	sed -i "s/^version.*/version = \"$(CURRENT_VERSION)\"/" pyproject.toml
	-git add .changes exbetapi/__init__.py pyproject.toml CHANGELOG.md
	-git commit -m "semverioner release updates" --no-verify
	-git flow release start $(CURRENT_VERSION)
	git flow release finish $(CURRENT_VERSION)

prerelease: test docs docs_store
release: prerelease semver clean check build upload git
