from pybibtex.parser import Parser

bibfile = """
@string(bibtex = "BiB\TeX")

BTXDOC:
@misc{bibtexing,
       author = "Oren Patashnik",
       title = bibtex # "ing",
       year = 1988,
       url = "https://www.ctan.org/tex-archive/biblio/bibtex/contrib/doc/"
}

Yes, between items, you can write whatever you want ;)
"""

parser = Parser(bibfile)
database = parser.parse()

# you can access the string variables after `parse()`
print(parser.string_variables['bibtex'])  # prints "BiB\TeX"

# you can access the items
assert 'bibtexing' in database
item = database['bibtexing']

# Note that the cite key is case insensitive
item = database['BiBTEXing']  # gives the same result

# you can access the fields
assert 'title' in item
print(item['title'])  # prints "BiB\TeXing", demonstrating concatenation
print(item['year'])  # prints 1988. Note that this is still a string.

# and you can access the item type and citation key
print('type: {}, cite key: {}'.format(item.item_type, item.cite_key))  # prints "type: misc, cite key: bibtexing"
