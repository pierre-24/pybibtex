Example of usage:

```python
from pybibtex.parser import Parser

bibtex = """
@string(bibtex = "BiB{\TeX}")
@misc{bibtexing,
   author = "Oren Patashnik",
   title = bibtex # "ing",
   year = 1988
}
"""

parser = Parser(bibtex)
database = parser.parse()

# access to item
assert 'bibtexing' in database

# you can access the string variables after `parse()`
print(parser.string_variables['bibtex'])  # prints "BiB{\TeX}"
```

::: pybibtex.parser