import unittest
from typing import Tuple, List

import pybibtex.parser as P
from pybibtex.bibliography import Database
from pybibtex.latexutf8 import utf8decode, utf8encode, LtxUTF8Parser
from pybibtex.authors import AuthorsParser, Author


class LiteralTestCase(unittest.TestCase):
    @staticmethod
    def parse_literal(text) -> str:
        return P.Parser(text).literal()

    def test_parse_alpha_literal(self):
        lit = 'test'
        self.assertEqual(self.parse_literal(lit), lit)

    def test_parse_alphanum_literal(self):
        lit = '_test12'
        self.assertEqual(self.parse_literal(lit), lit)

    def test_parse_literal_err(self):
        lit = 'test_12'

        self.assertEqual(self.parse_literal('{} x'.format(lit)), lit)  # space
        self.assertEqual(self.parse_literal('{}-x'.format(lit)), lit)  # char

        # cannot start by things outside [a-zA-Z_]
        with self.assertRaises(P.ParserSyntaxError):
            self.parse_literal('!test')

        # cannot start by a numeric char
        with self.assertRaises(P.ParserSyntaxError):
            self.parse_literal('1word')


class FieldTestCase(unittest.TestCase):
    @staticmethod
    def parse_field(text) -> Tuple[str, str]:
        return P.Parser(text).field()

    def test_parse_value_dquote(self):
        item_key, item_val = 'abc', 'de f'
        key, val = self.parse_field('{} = "{}"'.format(item_key, item_val))

        self.assertEqual(item_key, key)
        self.assertEqual(item_val, val)

    def test_parse_value_braced(self):
        item_key, item_val = 'abc', 'de f'
        key, val = self.parse_field('{} = {{{}}}'.format(item_key, item_val))

        self.assertEqual(item_key, key)
        self.assertEqual(item_val, val)

    def test_parse_value_dquote_escaped(self):
        item_key, item_val = 'abc', 'de {"} f'
        key, val = self.parse_field('{} = "{}"'.format(item_key, item_val))

        self.assertEqual(item_key, key)
        self.assertEqual(item_val, val)

    def test_parse_value_multi_braced(self):
        item_key, item_val = 'abc', 'd{e} f'
        key, val = self.parse_field('{} = {{{}}}'.format(item_key, item_val))

        self.assertEqual(item_key, key)
        self.assertEqual(item_val, val)

    def test_parse_value_int(self):
        item_key, item_val = 'abc', 3
        key, val = self.parse_field('{} = {}'.format(item_key, item_val))

        self.assertEqual(item_key, key)
        self.assertEqual('{}'.format(item_val), val)


class ParserTestCase(unittest.TestCase):
    @staticmethod
    def parse(text):
        return P.Parser(text).parse()

    def test_parse_one_item_noval(self):
        item_type = 'article'
        item_name = 'test'

        database = '@{}{{{}, }}'.format(item_type, item_name)
        result = self.parse(database)

        self.assertTrue(len(result.db) == 1)
        self.assertIn(item_name, result.db)

        item = result.db[item_name]
        self.assertEqual(item.cite_key, item_name)
        self.assertEqual(item.item_type, item_type)
        self.assertTrue(len(item.fields) == 0)

    def test_parse_one_item_parenthesis(self):
        item_type = 'article'
        item_name = 'test'

        database = '@{}({}, )'.format(item_type, item_name)

        result = self.parse(database)
        self.assertTrue(len(result.db) == 1)

    def test_parse_one_item_and_comment(self):
        item_type = 'article'
        item_name = 'test'

        database = '@{}{{{}, }}  @comment{{\nwhatever}}'.format(
            item_type, item_name)
        result = self.parse(database)

        self.assertTrue(len(result.db) == 1)
        self.assertIn(item_name, result.db)

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
        self.assertEqual(item.cite_key, item_name)
        self.assertEqual(item.item_type, item_type)
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
        self.assertEqual(result.db[item1_name].item_type, item1_type)
        self.assertEqual(result.db[item2_name].item_type, item2_type)

    def test_two_items_noval_and_comment(self):
        item1_type = 'article'
        item1_name = 'test1'
        item2_type = 'book'
        item2_name = 'test2'

        database = '@{}{{{}, }} this is a comment !!! @{}{{{}, }}'.format(
            item1_type, item1_name, item2_type, item2_name)

        result = self.parse(database)
        self.assertTrue(len(result.db) == 2)
        self.assertEqual(result.db[item1_name].item_type, item1_type)
        self.assertEqual(result.db[item2_name].item_type, item2_type)

    def test_one_item_atcomment_one_item(self):
        item1_type = 'article'
        item1_name = 'test1'
        item2_type = 'book'
        item2_name = 'test2'

        database = '@{}{{{}, }}\n@comment{{whatever @article{{\n fits your boat }} @{}{{{}, }}'.format(
            item1_type, item1_name, item2_type, item2_name)

        result = self.parse(database)
        self.assertTrue(len(result.db) == 2)
        self.assertEqual(result.db[item1_name].item_type, item1_type)
        self.assertEqual(result.db[item2_name].item_type, item2_type)

    def test_output(self):
        db1 = self.parse('@misc(item1, key = {val{u}e}) @misc(item2, key = "valu{"}e{"}")')
        db2 = self.parse(str(db1))

        # test if output is equals to input after parse
        self.assertEqual(len(db1.db), len(db2.db))

        for i1 in db1.db.values():
            self.assertIn(i1.cite_key, db2)
            i2 = db2[i1.cite_key]

            self.assertEqual(i1.item_type, i2.item_type)

            for k1 in i1.fields:
                self.assertIn(k1, i2.fields)
                self.assertEqual(i1.fields[k1], i2.fields[k1])


class ParserStringTestCase(unittest.TestCase):
    @staticmethod
    def parse(text) -> Tuple[Database, dict]:
        parser = P.Parser(text)
        db = parser.parse()

        return db, parser.string_variables

    def test_string_def(self):
        key = 'tmp'
        val = 'xyz'

        db, defs = self.parse('@string({} = "{}")'.format(key, val))

        self.assertEqual(defs[key], val)

    def test_string_use(self):
        key = 'tmp'
        val = 'xyz'

        db, defs = self.parse('@string({k} = "{v}") @article(whatever, key = {k})'.format(**{'k': key, 'v': val}))

        self.assertEqual(defs[key], val)
        self.assertEqual(db['whatever'].fields['key'], val)

    def test_string_concatenate(self):
        key1 = 'tmp'
        val1 = 'xyz'
        key2 = '_whatever'
        val2 = 'abc'
        val_in = 'efg'

        db, defs = self.parse(
            '@string({k1} = "{v1}") @string({k2} = "{v2}") @article(whatever, key = {k1} # "{vi}" # {k2})'.format(
                **{'k1': key1, 'v1': val1, 'k2': key2, 'v2': val2, 'vi': val_in}))

        self.assertEqual(defs[key1], val1)
        self.assertEqual(db['whatever'].fields['key'], val1 + val_in + val2)


class LaTeXUTF8TestCase(unittest.TestCase):

    @staticmethod
    def transform(inp: str, macros: dict) -> str:
        return LtxUTF8Parser(inp, macros).transform()

    def test_macro_noarg(self):
        macro_def = {
            'x': 233  # = é
        }

        self.assertEqual(self.transform('plant\\x, le sapin', macro_def), 'planté, le sapin')

        str_in = 'plant\\y'  # unknown macro → left as is!
        self.assertEqual(self.transform(str_in, macro_def), str_in)

    def test_macro_with_arg(self):
        macro_def = {
            'xe': {
                'a': 232,  # = è
                'b': 233  # = é
            }
        }

        self.assertEqual(self.transform('plant\\xe{b} un arbre', macro_def), 'planté un arbre')
        self.assertEqual(self.transform('m\\xe are', macro_def), 'mère')  # equivalent to `m\xe{a}re`

    def test_nonalpha_macro_with_arg(self):
        macro_def = {
            '^': {
                'a': 226,  # = â
                'e': 234  # = ê
            }
        }

        self.assertEqual(self.transform('\\^etre', macro_def), 'être')
        self.assertEqual(self.transform('gr\\^ace', macro_def), 'grâce')

    def test_remove_braces_for_enclosed_macro(self):
        macro_def = {
            'x': 233,  # = é
            'y': {
                'a': 233  # = é
            },
            "'": {
                'e': 233  # = é
            }
        }

        # test the different forms of macros:
        self.assertEqual(self.transform('mang{\\x}', macro_def), 'mangé')
        self.assertEqual(self.transform("mang{\\'e}", macro_def), 'mangé')
        self.assertEqual(self.transform('mang{\\y a}', macro_def), 'mangé')
        self.assertEqual(self.transform('mang{\\y{a}}', macro_def), 'mangé')

    # test the two API functions:
    TEST_IN = "Cet été, j'ai été à la chasse aux mûres"
    TEST_OUT = "Cet \\'et\\'e, j'ai \\'et\\'e \\`a la chasse aux m\\^ures"

    def test_decode(self):
        self.assertEqual(utf8decode(self.TEST_IN), self.TEST_OUT)

    def test_encode(self):
        self.assertEqual(utf8encode(self.TEST_OUT), self.TEST_IN)


class AuthorsTestCase(unittest.TestCase):

    @staticmethod
    def transform(inp: str) -> List[Author]:
        return AuthorsParser(inp).authors()

    @staticmethod
    def word(inp: str) -> Tuple[str, int]:
        return AuthorsParser(inp).word()

    def test_capitalization(self):
        word = 'test'
        self.assertEqual(self.word(word), (word, 0))

        word = 'Test'
        self.assertEqual(self.word(word), (word, 1))

        word = "{\\'E}"
        self.assertEqual(self.word(word), (word, 1))  # special characters has the case of their argument

        word = "{\\'e}"
        self.assertEqual(self.word(word), (word, 0))

        word = '{\\x{É}}'
        self.assertEqual(self.word(word), (word, 1))

        word = '{\\x{é}}'
        self.assertEqual(self.word(word), (word, 0))

        word = '{\\x}'
        self.assertEqual(self.word(word), (word, -1))  # this is special character, but it has no argument, so caseless

        word = '{E}'
        self.assertEqual(self.word(word), (word, -1))  # BRACEDITEM has no case!

        word = "{{\\'E}}"
        self.assertEqual(self.word(word), (word, -1))  # this is NOT a special character (two pairs of braces)

        word = '{É}cole'
        self.assertEqual(self.word(word), (word, 0))  # BRACEDITEM has no case, so the next letter is taken

    def test_one_author_natural_form(self):
        print(self.transform('Phillipe de Belgique'))

    def test_one_author_colon_form(self):
        print(self.transform('de Belgique, Phillipe'))

    def test_one_author_colon_form_pseudoletter(self):
        print(self.transform("de Flandre, {\\'E}mile"))

    def test_multi_authors_natural_form(self):
        print(self.transform('Phillipe de Belgique and Pierre Beaujean'))

    def test_multi_authors_colon_form(self):
        print(self.transform('de Belgique, Phillipe and Beaujean, Pierre'))
