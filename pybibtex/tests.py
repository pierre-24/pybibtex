import unittest
from typing import Tuple

import pybibtex.parser as P


class ParserTestCase(unittest.TestCase):

    @staticmethod
    def parse_val(text) -> Tuple[str, str]:
        return P.Parser(text).value()

    def test_parse_value_squote(self):
        item_key, item_val = 'abc', 'de f'
        key, val = self.parse_val("{} = '{}'".format(item_key, item_val))

        self.assertEqual(item_key, key)
        self.assertEqual(item_val, val)

    def test_parse_value_squote_escaped(self):
        item_key, item_val = 'abc', "de\\' f"
        key, val = self.parse_val("{} = '{}'".format(item_key, item_val))

        self.assertEqual(item_key, key)
        self.assertEqual(item_val, val)

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
        self.assertEqual(item.item_type, item_type)
        self.assertTrue(len(item.values) == 0)

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
        self.assertEqual(item.item_type, item_type)
        self.assertTrue(len(item.values) == 2)
        self.assertIn(item_k1_key, item.values)
        self.assertEqual(item.values[item_k1_key], item_k1_value)
        self.assertIn(item_k2_key, item.values)
        self.assertEqual(item.values[item_k2_key], item_k2_value)
