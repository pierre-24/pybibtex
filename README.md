# `pybibtex`: a simple BibTeX parser

Provides a Python API to parse BibTeX files.
Not to be confused with the (actual) [`pybibtex`](https://github.com/rasbt/pybibtex): this one is a more clever (this is actual parsing), but it does not contains any tools (yet?).

**Note:** BibTeX syntax is described with some details [here](https://www.bibtex.com/g/bibtex-format/) and in [`btxdoc`](https://www.ctan.org/tex-archive/biblio/bibtex/contrib/doc/) (and some quirks are examplified [here](http://artis.imag.fr/~Xavier.Decoret/resources/xdkbibtex/bibtex_summary.html)).
This version handles the different syntax for the items (braces or parentheses) and the concatenation (with the `@string` definition).


# Install 

```bash
pip install --upgrade git+https://github.com/pierre-24/pybibtex.git
```

No dependencies are required (except python, of course).

See a minimal working example [there](example.py) demonstrating the (quite simple) API.

## Contributions

Contributions, either with [issues](https://github.com/pierre-24/pybibtex/issues) or [pull requests](https://github.com/pierre-24/pybibtex/pulls) are welcomed.

If you can to contribute, this is the usual deal: 
start by [forking](https://guides.github.com/activities/forking/), then clone your fork

```bash
git clone git@github.com:<YOUR_USERNAME>/pybibtex.git
cd pybibtex
```

Then setup... And you are good to go :)

```bash
python -m venv venv # a virtualenv is always a good idea
source venv/bin/activate
make init  # install what's needed for dev
```

Don't forget to work on a separate branch, and to run the linting and tests:

```bash
make lint  # flake8
make test  # unit tests
```