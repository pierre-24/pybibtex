from typing import Dict


class Item:
    """Note: `item_type` and `cite_key` are case technically case insensitive, but the actual `cite_key` is kept

    """
    def __init__(self, cite_key: str, item_type: str = 'article', fields: dict = None):
        self.cite_key = cite_key
        self.item_type = item_type.lower()
        self.fields = fields

    def __repr__(self):
        return "Item('{}', '{}')".format(self.cite_key, self.item_type)

    def __getitem__(self, item: str) -> str:
        return self.fields[item]

    def __contains__(self, item: str) -> bool:
        return item in self.fields


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
