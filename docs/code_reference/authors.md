Example of usage:

```python
from pybibtex.authors import AuthorsParser

authors = AuthorsParser(
    'Pierre Beaujean and de la Fontaine, Jean').authors()

assert len(authors) == 2

print(authors[0].last)  # prints "Beaujean"
print(
    authors[1].first,
    authors[1].von, 
    authors[1].last)  # prints "Jean de la Fontaine"
```

::: pybibtex.authors