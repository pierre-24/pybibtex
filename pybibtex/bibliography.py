from typing import Dict


class Item:
    def __init__(self, key: str, entry_type: str = 'article', fields: dict = None):
        self.key = key.lower()
        self.entry_type = entry_type.lower()
        self.fields = fields

    def __repr__(self):
        return "Item('{}', '{}')".format(self.key, self.entry_type)


class Database:
    """Database of bibliographic items"""
    def __init__(self, db: Dict[str, Item] = None):
        self.db = {} if db is None else db

    def __getitem__(self, item: str) -> Item:
        return self.db[item]
