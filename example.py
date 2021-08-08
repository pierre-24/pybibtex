from pybibtex.parser import Parser

bibfile = """
@string(bibtex = "BiB\TeX")

@comment that's a comment

@misc{bibtexing,
       author = "Oren Patashnik",
       title = bibtex # "ing",
       year = 1988,
       url = {https://www.ctan.org/tex-archive/biblio/bibtex/contrib/doc/}
}

Yes, between items you can write whatever you want, it's comment as well ;)
"""

parser = Parser(bibfile)
database = parser.parse()

# you can access the string variables after `parse()`
print(parser.string_variables['bibtex'])  # prints "BiB\TeX"

# you can access the items
assert 'bibtexing' in database
item = database['bibtexing']
item = database['BiBTEXing']  # the cite keys are case insensitive, this gives the same result!

# you can access the fields
assert 'title' in item
print(item['title'])  # prints "BiB\TeXing", demonstrating concatenation
print(item['year'])  # prints "1988". Note that this is still a string.

# ... and you can access the item type and citation key
print('type: {}, cite key: {}'.format(item.item_type, item.cite_key))  # prints "type: misc, cite key: bibtexing"

# you can access the authors with a practical API
authors = item.authors()
print('first name: {}, last name: {}'.format(
    authors[0].first, authors[0].last))  # prints "first name: Oren, last name: Patashnik"

# outputs
print(database)  # Note: the output is not lossless, since comments are lost and concatenations are applied
