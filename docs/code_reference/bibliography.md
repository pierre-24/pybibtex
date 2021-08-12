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

database = Parser(bibtex).parse()

item = database['bibtexing']

print(item['title'])  # prints "BiB{\TeX}ing
print(item['year'])  # prints 1988
```

::: pybibtex.bibliography
