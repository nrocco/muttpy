VIRTUAL_ENV ?= $(PWD)/env

PY = $(VIRTUAL_ENV)/bin/python
PIP = $(VIRTUAL_ENV)/bin/pip

current_version = $(shell $(PY) setup.py --version)
package_name = $(shell $(PY) setup.py --name)
init_py_file = $(package_name)/__init__.py


# Create a virtualenv if not in one already
$(PY):
	virtualenv env
	$(eval VIRTUAL_ENV = $(PWD)/env)

# Build the source tarball
.PHONY: build
build: $(PY) clean
	$(PY) setup.py sdist


# Prepare the environment for development
.PHONY: develop
develop: $(PY) deps
	$(PY) setup.py develop


# install development dependencies
.PHONY: deps
deps: $(PY)
	if [ -f requirements.txt ]; then $(PIP) install -r requirements.txt; fi


# bump the version number
.PHONY: bump
bump: $(PY)
	@test ! -z "$(version)" || ( echo "specify a version number: make bump version=$(current_version)" && exit 1 )
	@! git status --porcelain 2> /dev/null | grep -v "^??" || ( echo 'uncommited changes. commit them first' && exit 1 )
	@echo "Bumping current version $(current_version) to $(version)"
	sed -i'.bak' -e "/^__version__ = .*$$/s/'[^']*'/'$(version)'/" $(init_py_file)
	rm -f $(init_py_file).bak
	git add $(init_py_file)
	git commit -m 'Bumped version number to $(version)'
	git tag -m 'Mark stable release version $(version)' -a $(version)
	@echo "Version $(version) commited and tagged. You can 'make push' or 'make upload' now :)"


# Fetch everything from github
.PHONY: fetch
pull:
	git fetch --all
	git fetch --tags


# Push to github but run tests first
.PHONY: push
push:
	git push origin HEAD
	git push origin --tags


# Clean all build artifacts
.PHONY: clean
clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '._*' -exec rm -f {} +
	find . -name '.coverage*' -exec rm -f {} +
	rm -rf build/ dist/ MANIFEST docs/_build/* 2>/dev/null || true
