Here are 3 example of the usage you can have of `pybibtex`.

## Import and use bibliography

Say you want to import this BibTeX file, stored in `example.bib`.

```bibtex
@string(bibtex = "BiB{\TeX}")

@comment that's a comment
@misc{bibtexing,
       author = "Oren Patashnik",
       title = bibtex # "ing",
       year = 1988,
       url = {https://www.ctan.org/tex-archive/biblio/bibtex/contrib/doc/}
}

Yes, between items, you can write whatever you want!
```

You can import this bibliography using

```python
from pybibtex.parser import Parser

with open('test.bib') as bibfile:
    database = Parser(bibfile.read()).parse()
```

You can check and access the items via their citation key:

```python
assert 'bibtexing' in database
item = database['bibtexing']
```

Note that per BibTeX specification, the citation key is case insensitive, so that the following code results in the same item:

```python
item = database['BiBTEXing']
```

A bibliography item contains the different fields, which are directly addressable:

```python
assert 'title' in item
print(item['title'])
print(item['year'])
```

This results in

```text
Bib\TeXing
1988
```

The first line demonstrate the concatenation at line 7 of test.bib. 
You can access the citation key with `item.cite_key` and the item type with `item.item_type`.

## Get authors

`pybibtex` provides a convenient API to extract the authors.

One way to use it is

```python
from pybibtex.authors import AuthorsParser
authors = AuthorsParser(
    'Pierre Beaujean and de la Fontaine, Jean').authors()
```
   

But you can also access the author of a bibliography item with this specific function:

```python
authors = item.authors()
```

Both methods return a list of `Author`. You can then access

+ its last name, with `author.last` (always not empty),
+ its first name, with `author.first` (may be empty),
+ its "von" part, with `author.von` (may be empty),
+ its "jr" part, with `author.jr` (may be empty).

## Convert accentuated strings

LaTeX is notoriously (in)famous for its way to handle UTF-8 characters.
You can convert a string to this format using

```python
from pybibtex.latexutf8 import utf8decode
print(utf8decode('Émile de la Tourbière'))
```

which outputs:

```text
\'Emile de la Tourbi\`ere
```

The converse is obtained with:

```python
from pybibtex.latexutf8 import utf8encode
print(utf8encode("\\'Emile de la Tourbi\\`ere"))
```