from typing import Dict


class Item:
    """Note: `item_type` and `cite_key` are case technically case insensitive, but the actual `cite_key` is kept

    """
    def __init__(self, cite_key: str, item_type: str = 'article', fields: dict = None):
        self.cite_key = cite_key
        self.item_type = item_type.lower()
        self.fields = fields

    def __repr__(self) -> str:
        return "Item('{}', '{}')".format(self.cite_key, self.item_type)

    def __getitem__(self, item: str) -> str:
        return self.fields[item]

    def __setitem__(self, key, value):
        self.fields[key] = value

    def __contains__(self, item: str) -> bool:
        return item in self.fields

    def __str__(self) -> str:
        """Outputs bibtex item
        """

        return '@{}{{{},\n  {}\n}}'.format(
            self.item_type,
            self.cite_key,
            ',\n  '.join('{} = "{}"'.format(k, v) for k, v in self.fields.items()))


class Database:
    """Database of bibliographic items

    Note: `cite_key` are considered to be case insensitive in lookup
    """

    def __init__(self, db: Dict[str, Item] = None):
        self.db = {} if db is None else db

    def __getitem__(self, item: str) -> Item:
        return self.db[item.lower()]

    def __contains__(self, item) -> bool:
        return item.lower() in self.db

    def __iter__(self):
        for item in self.db:
            yield item

    def __repr__(self):
        return ', '.join('@{}({})'.format(i.item_type, i.cite_key) for i in self.db.values())

    def __str__(self) -> str:
        """Outputs bibtex database
        """

        return '\n'.join(str(item) for item in self.db.values())
