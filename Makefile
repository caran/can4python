.PHONY: clean-pyc clean-build docs clean

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "clean-doc - remove documentation artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "vcan - Start Linux virtual CAN bus vcan0"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "pdf - generate PDF documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"

clean: clean-build clean-pyc clean-test clean-doc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	rm -fr can4python/__pycache__/
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	find . -name '*TEMPORARY.kcd' -exec rm -f {} +

clean-doc:
	rm -fr docs/_build
	-$(MAKE) -C docs clean
	
lint:
	flake8 can4python tests

test:
	python3 setup.py test

test-all:
	tox

vcan:
	modprobe vcan
	ip link add dev vcan0 type vcan
	ifconfig vcan0 up

coverage:
	coverage run --branch --source can4python setup.py test
	coverage report -m
	coverage html
	@echo "    "
	@echo "    "
	@echo "    "
	@echo "Opening web browser ..."
	xdg-open htmlcov/index.html

docs: clean-doc
	sphinx-apidoc -o docs/ can4python
	$(MAKE) -C docs html
	@echo "    "
	@echo "    "
	@echo "    "
	@echo "Opening web browser ..."
	xdg-open docs/_build/html/index.html

pdf: docs
	$(MAKE) -C docs latexpdf
	@echo "    "
	@echo "    "
	@echo "    "
	@echo "Opening PDF reader ..."
	xdg-open docs/_build/latex/can4python.pdf

release: clean
	python3 setup.py sdist upload
	python3 setup.py bdist_wheel upload

dist: clean
	python3 setup.py sdist
	python3 setup.py bdist_wheel
	ls -l dist

install: clean
	python3 setup.py install
