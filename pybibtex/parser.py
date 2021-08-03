from typing import Tuple, Iterator, Union
from enum import Enum, unique
import re

from bibliography import Database, Item


@unique
class TokenType(Enum):
    LCBRACE = '{'
    RCBRACE = '}'
    LPAR= '('
    RPAR = ')'
    SPACE = 'SPC'
    NL = 'NWL'
    EOS = '\0'
    CHAR = 'CHR'
    AT = '@'
    QUOTE = '"'
    COMMA = 'CMA'
    EQUAL = '='
    POUND = '#'


OPENINGS = (TokenType.LPAR, TokenType.LCBRACE)

SYMBOL_TR = {
    '{': TokenType.LCBRACE,
    '}': TokenType.RCBRACE,
    '(': TokenType.LPAR,
    ')': TokenType.RPAR,
    ' ': TokenType.SPACE,
    '@': TokenType.AT,
    '\t': TokenType.SPACE,
    '\n': TokenType.NL,
    '"': TokenType.QUOTE,
    ',': TokenType.COMMA,
    '=': TokenType.EQUAL,
    '#': TokenType.POUND
}


class Token:
    def __init__(self, typ_: TokenType, value: str, position: int = -1):
        self.type = typ_
        self.value = value
        self.position = position

    def __repr__(self):
        return 'Token({}, \'{}\'{})'.format(
            self.type,
            self.value,
            '' if self.position < 0 else ', {}'.format(self.position)
        )


class Lexer:
    def __init__(self, inp):
        self.input = inp
        self.position = -1
        self.current_char = None

        self.next()

    def next(self):
        """Go to next token
        """

        self.position += 1

        if self.position >= len(self.input):
            self.current_char = '\0'
        else:
            self.current_char = self.input[self.position]

    def tokenize(self) -> Iterator[Token]:
        while self.current_char != '\0':
            if self.current_char in SYMBOL_TR:
                yield Token(SYMBOL_TR[self.current_char], self.current_char, self.position)
            else:
                yield Token(TokenType.CHAR, self.current_char, self.position)
            self.next()

        yield Token(TokenType.EOS, '\0', self.position)


class ParserSyntaxError(Exception):
    pass


IS_LITERAL = re.compile(r'[a-zA-Z0-9_]')
IS_LITERAL_BEG = re.compile(r'[a-zA-Z_]')
IS_KEY = re.compile(r'[a-zA-Z0-9_\-:]')


class Parser:
    def __init__(self, inp: str):
        self.lexer = Lexer(inp)
        self.tokenizer = self.lexer.tokenize()
        self.current_token: Token = None

        self.string_variables = {}

        self.next()

    def _next(self):
        """Get next token"""

        try:
            self.current_token = next(self.tokenizer)
        except StopIteration:
            self.current_token = Token(TokenType.EOS, '\0')

    def next(self):
        """Get next token"""

        self._next()

    def eat(self, typ: TokenType):
        if self.current_token.type == typ:
            self.next()
        else:
            raise ParserSyntaxError('expected {}, got {}'.format(typ, self.current_token))

    def skip_empty(self):
        """Skip spaces, newlines and comments
        """

        while self.current_token.type in [TokenType.SPACE, TokenType.NL]:
            self.next()

    def skip_any_but_item(self):
        """Skip anything until the next @, since it is considered to be a comment
        """

        while self.current_token.type not in [TokenType.AT, TokenType.EOS]:
            self.next()

    def parse(self) -> Database:
        return self.database()

    def literal(self) -> str:
        """Get a literal, as

        ```
        literal := [a-aA-Z_] [a-zA-Z0-9_]*
        ```

        Note: it cannot start by an integer, for obvious reasons.
        """

        if self.current_token.type != TokenType.CHAR or not IS_LITERAL_BEG.match(self.current_token.value):
            raise ParserSyntaxError('expected literal, got {}'.format(self.current_token))

        literal = self.current_token.value
        self.next()

        while self.current_token.type == TokenType.CHAR and IS_LITERAL.match(self.current_token.value):
            literal += self.current_token.value
            self.next()

        return literal

    def key(self) -> str:
        """Get a key,

        ```
        key := [a-zA-Z0-9_\\-:]*
        ```

        Note: that means that a key can start by an integer or `:` (that should not be a problem)
        """

        if self.current_token.type != TokenType.CHAR or not IS_KEY.match(self.current_token.value):
            raise ParserSyntaxError('expected literal, got {}'.format(self.current_token))

        citekey = ''

        while self.current_token.type == TokenType.CHAR and IS_KEY.match(self.current_token.value):
            citekey += self.current_token.value
            self.next()

        return citekey

    def database(self) -> Database:
        """
        The BibTeX format is more or less defined as

        ```
        bibtex := (item | string_var | comment)*;
        ```

        with

        ```
        string_var := AT 'string' (LCBRACE inside_string_var RCBRACE | LPAR inside_string_var RPAR) ;
        item := AT literal (LCBRACE inside_item RCBRACE | LPAR inside_item RPAR) ;
        comment := (AT 'comment' CHAR* NL | CHAR*)
        ```

        (it is missing the `@preamble`).
        """

        db = {}
        self.skip_any_but_item()  # go to the next @

        while self.current_token.type != TokenType.EOS:
            self.eat(TokenType.AT)

            # get type
            item_type = self.literal()
            self.skip_empty()

            if item_type.lower() == 'comment':
                self.comment()
            else:
                # get opening
                if self.current_token.type not in OPENINGS:
                    raise ParserSyntaxError('expected OPENINGS, got {}'.format(self.current_token))

                opening = self.current_token.type
                closing = {
                    TokenType.LPAR: TokenType.RPAR,
                    TokenType.LCBRACE: TokenType.RCBRACE
                }[opening]

                self.next()
                self.skip_empty()

                # go inside
                if item_type.lower() == 'string':
                    self.inside_string_var()
                else:
                    item = self.inside_item(item_type)
                    db[item.cite_key.lower()] = item

                self.skip_empty()
                self.eat(closing)

            self.skip_any_but_item()

        self.eat(TokenType.EOS)
        return Database(db)

    def comment(self):
        """Skip whatever remains of the line
        """

        while self.current_token.type not in [TokenType.NL, TokenType.EOS]:
            self.next()

    def inside_string_var(self):
        """Defines a string variable:

        ```
        inside_string_var := key EQUAL value ;
        ```

        Note: `key` is maybe a bit broadly defined (is `:` valid?)
        """

        # get placeholder
        placeholder = self.literal()

        # eat EQUAL
        self.skip_empty()
        self.eat(TokenType.EQUAL)
        self.skip_empty()

        # get value and define
        value = self.value()
        self.string_variables[placeholder] = value

    def inside_item(self, item_type: str) -> Item:
        """Get an item:

        ```
        inside_item := key COMMA (field (COMMA field)*)? COMMA?
        ```
        """

        # get key
        item_citekey = self.key()

        # eat COMMA
        self.skip_empty()
        self.eat(TokenType.COMMA)
        self.skip_empty()

        # get fields
        fields = {}
        while True:

            if self.current_token.type == TokenType.COMMA:  # empty value, skip
                self.next()
                continue

            elif self.current_token.type in [TokenType.RCBRACE, TokenType.RPAR]:  # that's the end of it!
                break

            try:
                k, v = self.field()
            except ParserSyntaxError as e:
                raise ParserSyntaxError('while parsing {}, {}'.format(item_citekey, e))

            fields[k] = v

            self.skip_empty()
            if self.current_token.type != TokenType.COMMA:
                break
            else:
                self.next()
                self.skip_empty()

        return Item(cite_key=item_citekey, item_type=item_type, fields=fields)

    def field(self) -> Tuple[str, str]:
        """
        Get a field:

        ```
        field := key EQUAL value ;
        ```
        """

        # get key
        key = self.key()

        # eat EQUAL
        self.skip_empty()
        self.eat(TokenType.EQUAL)
        self.skip_empty()

        # get value and return
        return key, self.value()

    def value(self) -> str:
        """A value is a string, but different stuffs can be concatenated.

        ```
        value := string_part (POUND string_part)* ;
        ```

        Note: it means that integer can be concatenated, deal with it.
        """
        value = self.string_part()

        # concatenate?
        self.skip_empty()

        while self.current_token.type == TokenType.POUND:
            # eat POUND
            self.next()
            self.skip_empty()

            # get next value
            value += self.string_part()
            self.skip_empty()

        # ok, done
        return value

    def string_part(self) -> str:
        """Get an actual string.

        Note that for a quote to be escaped, it must be inside braces.
        Which means that braces **must** match, even in quote.
        
        ```
        INTEGER := [0-9]

        sl := CHAR*
           | QUOTE
           | LBRACE sl* RBRACE
           ;
        
        string_part := literal
                    | INTEGER INTEGER*
                    | LBRACE sl* RBRACE
                    | QQUOTE (CHAR* | LCBRACE sl* RCBRACE)* QUOTE
                    ;
        ```
        """

        if self.current_token.type == TokenType.CHAR:
            if self.current_token.value.isnumeric():  # its a pure integer
                value = ''
                while self.current_token.type == TokenType.CHAR and self.current_token.value.isnumeric():
                    value += self.current_token.value
                    self.next()
            else:  # ... it is a literal, then
                lit = self.literal()
                try:
                    value = self.string_variables[lit]
                except KeyError:
                    raise ParserSyntaxError('{} is not defined'.format(lit))

        elif self.current_token.type in [TokenType.LCBRACE, TokenType.QUOTE]:
            opening_char = self.current_token.type
            self.next()

            value = ''
            brace_level = 1 if opening_char == TokenType.LCBRACE else 0
            while True:
                if self.current_token.type == TokenType.LCBRACE:
                    brace_level += 1
                elif self.current_token.type == TokenType.RCBRACE:
                    brace_level -= 1
                    if opening_char == TokenType.LCBRACE and brace_level == 0:
                        self.next()
                        break
                elif self.current_token.type == TokenType.QUOTE:
                    if opening_char == TokenType.QUOTE and brace_level == 0:
                        self.next()
                        break
                elif self.current_token.type == TokenType.EOS:
                    raise ParserSyntaxError('got {} while parsing string'.format(self.current_token))

                value += self.current_token.value
                self.next()
        else:
            raise ParserSyntaxError('expected string, got {}'.format(self.current_token))

        return value
