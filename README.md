# `pybibtex`: a (very) simple BibTeX parser

Provides a Python API to parse BibTeX files.
Not to be confused with the (actual) [`pybibtex`](https://github.com/rasbt/pybibtex), which uses REGEX, while this implementation use an actual LL(1) parser (less error-prone, normally).

The BiBTeX syntax is introduced, simply, [there](https://www.bibtex.com/g/bibtex-format/).
More details are found in [`btxdoc`](https://www.ctan.org/tex-archive/biblio/bibtex/contrib/doc/) (and some of its quirks are examplified [here](http://artis.imag.fr/~Xavier.Decoret/resources/xdkbibtex/bibtex_summary.html)).
This implementation handles the different syntax for the items (braces or parentheses), the comments, and the concatenation (with the `@string` definitions).
It does not handle `@preamble`.


## Install & use

```bash
pip3 install --upgrade git+https://github.com/pierre-24/pybibtex.git@v0.2.1
```

No dependencies are required (except python >= 3.6).

See the documentation [there](https://pierre-24.github.io/pybibtex/usage/) demonstrating the (quite simple) API.

## Contribute

Contributions, either with [issues](https://github.com/pierre-24/pybibtex/issues) or [pull requests](https://github.com/pierre-24/pybibtex/pulls) are welcomed.
See the [Contributing section](https://pierre-24.github.io/pybibtex/contributing/) of the documentation for more details.