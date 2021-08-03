import unittest
from typing import Tuple

import pybibtex.parser as P


class ParserTestCase(unittest.TestCase):

    @staticmethod
    def parse_val(text) -> Tuple[str, str]:
        return P.Parser(text).field()

    def test_parse_empty(self):
        key, val = self.parse_val(',')
        self.assertEqual(key, '')
        self.assertEqual(val, '')

    def test_parse_value_dquote(self):
        item_key, item_val = 'abc', 'de f'
        key, val = self.parse_val('{} = "{}"'.format(item_key, item_val))

        self.assertEqual(item_key, key)
        self.assertEqual(item_val, val)

    def test_parse_value_braced(self):
        item_key, item_val = 'abc', 'de f'
        key, val = self.parse_val('{} = {{{}}}'.format(item_key, item_val))

        self.assertEqual(item_key, key)
        self.assertEqual(item_val, val)

    def test_parse_value_braced_escaped(self):
        item_key, item_val = 'abc', 'de\\} f'
        key, val = self.parse_val('{} = {{{}}}'.format(item_key, item_val))

        self.assertEqual(item_key, key)
        self.assertEqual(item_val, val)

    def test_parse_value_multi_braced(self):
        item_key, item_val = 'abc', 'd{e} f'
        key, val = self.parse_val('{} = {{{}}}'.format(item_key, item_val))

        self.assertEqual(item_key, key)
        self.assertEqual(item_val, val)

    @staticmethod
    def parse(text):
        return P.Parser(text).parse()

    def test_parse_one_item_noval(self):
        item_type = 'article'
        item_name = 'test'

        database = '@{}{{{}, }}'.format(
            item_type, item_name)
        result = self.parse(database)

        self.assertTrue(len(result.db) == 1)
        self.assertIn(item_name, result.db)

        item = result.db[item_name]
        self.assertEqual(item.key, item_name)
        self.assertEqual(item.entry_type, item_type)
        self.assertTrue(len(item.fields) == 0)

    def test_parse_one_item_multival(self):
        item_type = 'article'
        item_name = 'test'
        item_k1_key = 'abc'
        item_k1_value = 'de f'
        item_k2_key = 'ijh'
        item_k2_value = 'test@xyz'

        database = '@{}{{{}, {} = "{}", {} = "{}", }}'.format(
            item_type, item_name, item_k1_key, item_k1_value, item_k2_key, item_k2_value)

        result = self.parse(database)

        self.assertTrue(len(result.db) == 1)
        self.assertIn(item_name, result.db)

        item = result.db[item_name]
        self.assertEqual(item.key, item_name)
        self.assertEqual(item.entry_type, item_type)
        self.assertTrue(len(item.fields) == 2)
        self.assertIn(item_k1_key, item.fields)
        self.assertEqual(item.fields[item_k1_key], item_k1_value)
        self.assertIn(item_k2_key, item.fields)
        self.assertEqual(item.fields[item_k2_key], item_k2_value)

    def test_two_items_noval(self):
        item1_type = 'article'
        item1_name = 'test1'
        item2_type = 'book'
        item2_name = 'test2'

        database = '@{}{{{}, }} @{}{{{}, }}'.format(
            item1_type, item1_name, item2_type, item2_name)

        result = self.parse(database)

        self.assertTrue(len(result.db) == 2)

    def test_two_items_noval_and_comment(self):
        item1_type = 'article'
        item1_name = 'test1'
        item2_type = 'book'
        item2_name = 'test2'

        database = '@{}{{{}, }} this is a comment !!! @{}{{{}, }}'.format(
            item1_type, item1_name, item2_type, item2_name)

        result = self.parse(database)

        self.assertTrue(len(result.db) == 2)
