Example of usage:

```python
from pybibtex.latexutf8 import utf8decode, utf8encode

# prints "\'Emile de la Tourbi\`ere"
print(utf8decode('Émile de la Tourbière')) 

# prints "Émile de la Tourbière"
print(utf8encode("\\'Emile de la Tourbi\\`ere"))
```


::: pybibtex.latexutf8
    selection:
      members:
        - utf8encode
        - utf8decode
        - UTF8EncodeException