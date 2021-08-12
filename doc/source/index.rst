
``pybibtex``
============

Provides a Python API to parse BibTeX files.

.. note::
   BibTeX syntax is introduced, simply, `there <https://www.bibtex.com/g/bibtex-format/>`_ and with more details in `btxdoc <https://www.ctan.org/tex-archive/biblio/bibtex/contrib/doc/>`_ (and some of its quirks are examplified `here <http://artis.imag.fr/~Xavier.Decoret/resources/xdkbibtex/bibtex_summary.html>`_).

   This implementation handles the different syntax for the items (braces or parentheses), the comments, and the concatenation (with the ``@string`` definitions).

Example usage
-------------

Import and use bibliography
+++++++++++++++++++++++++++

Says that you have the following BibTeX bibliography file:

.. literalinclude:: snippets/test.bib
    :caption: ``test.bib``
    :language: bibtex
    :linenos:
    :emphasize-lines: 7

You can import this bibliography using

.. code-block:: python

    from pybibtex.parser import Parser

    with open('test.bib') as bibfile:
        database = Parser(bibfile.read()).parse()

If no ``ParserSyntaxError`` is raised, then the bibliography items are imported.

You can check and access the items via their citation key:

.. code-block:: python

    assert 'bibtexing' in database
    item = database['bibtexing']

Note that per BibTeX specification, the citation key is case insensitive, so that the following code results in the same item:

.. code-block:: python

    item = database['BiBTEXing']

A bibliography item contains the different ``fields``,
which are directly addressable:

.. code-block:: python

    assert 'title' in item
    print(item['title'])
    print(item['year'])

This results in

.. code-block:: text

    Bib\TeXing
    1988

The first line demonstrate the concatenation at line 7 of ``test.bib``.
You can access the citation key with ``item.cite_key`` and the item type with ``item.item_type``.

Get authors
+++++++++++

``pybibtex`` provides a convenient API to extract the authors.

One way to use it is

.. code-block:: python

    from pybibtex.authors import AuthorsParser
    authors = AuthorsParser(
        'Pierre Beaujean and de la Fontaine, Jean').authors()

But you can also access the author of a bibliography item with this specific function:

.. code-block:: python

    authors = item.authors()

Both methods return a list of ``Author``. You can then access

+ its last name, with ``author.last`` (always not empty),
+ its first name, with ``author.first`` (may be empty),
+ its "von" part, with ``author.von`` (may be empty),
+ its "jr" part, with ``author.jr`` (may be empty).


Convert accentuated strings
+++++++++++++++++++++++++++

LaTeX is notoriously famous for its way to handle UTF-8 characters.
You can convert a string to this format using

.. code-block:: python

    from pybibtex.latexutf8 import utf8decode
    print(utf8decode('Émile de la Tourbière'))



which outputs:

.. code-block::

    \'Emile de la Tourbi\`ere

The converse is obtained with:

.. code-block:: python

    from pybibtex.latexutf8 import utf8encode
    print(utf8encode("\\'Emile de la Tourbi\\`ere"))


API documentation
-----------------

Bibliography and items
++++++++++++++++++++++

.. automodule:: pybibtex.bibliography
    :members:


Authors
+++++++

.. automodule:: pybibtex.authors
    :members:


UTF-8 stuffs
++++++++++++

.. automodule:: pybibtex.latexutf8
    :members:



Bibliography parser
+++++++++++++++++++

.. automodule:: pybibtex.parser
    :members: