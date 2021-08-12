# `pybibtex`: a (very) simple BibTeX parser

Provides a Python API to parse BibTeX files.
Not to be confused with the (actual) [`pybibtex`](https://github.com/rasbt/pybibtex): while this implementation is a more clever approach (this is actual syntax parsing, see [there](./pybibtex/parser.py)), but it does not provide any tools (yet?).

**Note:** BibTeX syntax is introduced, simply, [there](https://www.bibtex.com/g/bibtex-format/) and with more details in [`btxdoc`](https://www.ctan.org/tex-archive/biblio/bibtex/contrib/doc/) (and some of its quirks are examplified [here](http://artis.imag.fr/~Xavier.Decoret/resources/xdkbibtex/bibtex_summary.html)).
This implementation handles the different syntax for the items (braces or parentheses), the comments, and the concatenation (with the `@string` definitions).


## Install & use

```bash
pip3 install --upgrade git+https://github.com/pierre-24/pybibtex.git
```

No dependencies are required (except python >= 3.6).

See the documentation [there](doc/source/index.rst) demonstrating the (quite simple) API.

## Contribute

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

You can also build the documentation with

```bash
make docs
```