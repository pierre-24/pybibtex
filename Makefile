all: help

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  init                        to install python dependencies"
	@echo "  lint                        to lint backend code (flake8)"
	@echo "  test                        to run test suite"
	@echo "  help                        to get this help"
	@echo "  doc                         to build documentation"

init:
	pip install -e . && pip install -r requirements.txt

lint:
	flake8 pybibtex --max-line-length=120 --ignore=N802 --extend-exclude="_utf8translate.py"

test:
	python -m unittest discover -s pybibtex.tests

doc:
	mkdocs build
