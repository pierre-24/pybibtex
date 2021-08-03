from typing import Tuple, Iterator
from enum import Enum, unique
import re

from bibliography import Database, Item


@unique
class TokenType(Enum):
    BACKSLASH = '\\'
    LCBRACE = '{'
    RCBRACE = '}'
    LPAR= '('
    RPAR = ')'
    SPACE = 'SPC'
    NL = 'NWL'
    EOS = '\0'
    CHAR = 'CHR'
    AT = '@'
    DQUOTE = '"'
    COMMA = 'CMA'
    EQUAL = '='


OPENINGS = (TokenType.LPAR, TokenType.LCBRACE)

SYMBOL_TR = {
    '\\': TokenType.BACKSLASH,
    '{': TokenType.LCBRACE,
    '}': TokenType.RCBRACE,
    '(': TokenType.LPAR,
    ')': TokenType.RPAR,
    ' ': TokenType.SPACE,
    '@': TokenType.AT,
    '\t': TokenType.SPACE,
    '\n': TokenType.NL,
    '"': TokenType.DQUOTE,
    ',': TokenType.COMMA,
    '=': TokenType.EQUAL
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
        """Get a literal, as `[a-aA-Z_][a-zA-Z0-9_]*`
        """

        if self.current_token.type != TokenType.CHAR or not IS_LITERAL_BEG.match(self.current_token.value):
            raise ParserSyntaxError('expected literal, got {}'.format(self.current_token))

        literal = self.current_token.value
        self.next()

        while self.current_token.type == TokenType.CHAR and IS_LITERAL.match(self.current_token.value):
            literal += self.current_token.value
            self.next()

        return literal

    def database(self) -> Database:

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
                    self.string_var()
                else:
                    item = self.item(item_type)
                    db[item.key] = item

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

    def string_var(self):
        """Defines a string variable:

        ```
        inside_string_var := key EQUAL string ;
        ```
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

    def item(self, item_type: str) -> Item:
        """Get an item:

        ```
        inside_item := key COMMA (field (COMMA field)*)? COMMA?
        ```
        """

        # get key
        item_key = self.literal()

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
                raise ParserSyntaxError('while parsing {}, {}'.format(item_key, e))

            fields[k] = v

            self.skip_empty()
            if self.current_token.type != TokenType.COMMA:
                break
            else:
                self.next()
                self.skip_empty()

        return Item(key=item_key, entry_type=item_type, fields=fields)

    def field(self) -> Tuple[str, str]:
        """
        Get a field:

        ```
        field := key EQUAL value ;
        ```
        """

        # get key (key is more broad than a literal, since it can contains things like dash)
        key = ''
        while self.current_token.type == TokenType.CHAR:
            key += self.current_token.value
            self.next()

        # eat EQUAL
        self.skip_empty()
        self.eat(TokenType.EQUAL)
        self.skip_empty()

        # get value and return
        return key, self.value()

    def value(self) -> str:
        """A value is either a string or an int. Currently, only strings!

        ```
        value := INTEGER INTEGER*
              | LCBRACE CHAR* RCBRACE
              | DQUOTE CHAR* DQUOTE
              ;
        ```
        """

        if self.current_token.type not in [TokenType.LCBRACE, TokenType.DQUOTE]:
            raise ParserSyntaxError('expected string, got {}'.format(self.current_token))

        opening_char = self.current_token.type
        self.next()

        value = ''
        brace_level = 1 if opening_char == TokenType.LCBRACE else 0
        while True:
            if self.current_token.type == TokenType.BACKSLASH:  # escape next character, whatever it is
                self.next()
                value += '\\' + self.current_token.value
                self.next()
                continue
            elif self.current_token.type == TokenType.LCBRACE:
                brace_level += 1
            elif self.current_token.type == TokenType.RCBRACE:
                brace_level -= 1
                if opening_char == TokenType.LCBRACE and brace_level == 0:
                    self.next()
                    break
            elif self.current_token.type == TokenType.DQUOTE:
                if brace_level != 0:
                    raise ParserSyntaxError('unmatched braces while parsing {}'.format(key))
                self.next()
                break

            value += self.current_token.value
            self.next()

        return value
