from typing import Dict


class Item:
    def __init__(self, key: str, item_type: str = 'article', values: dict = None):
        self.key = key
        self.item_type = item_type
        self.values = values


class Database:
    """Database of bibliographic items"""
    def __init__(self, db: Dict[str, Item] = None):
        self.db = {} if db is None else db

    def __getitem__(self, item: str) -> Item:
        return self.db[item]
