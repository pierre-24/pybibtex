from typing import Tuple, Iterator
from enum import Enum, unique

from bibliography import Database, Item


@unique
class TokenType(Enum):
    BACKSLASH = '\\'
    LCBRACE = '{'
    RCBRACE = '}'
    PERCENT = '%'
    SPACE = 'SPC'
    NL = 'NWL'
    EOS = '\0'
    CHAR = 'CHR'
    AT = '@'
    SQUOTE = '\''
    DQUOTE = '"'
    COMMA = 'CMA'
    EQUAL = '='


SYMBOL_TR = {
    '\\': TokenType.BACKSLASH,
    '{': TokenType.LCBRACE,
    '}': TokenType.RCBRACE,
    '%': TokenType.PERCENT,
    ' ': TokenType.SPACE,
    '@': TokenType.AT,
    '\t': TokenType.SPACE,
    '\n': TokenType.NL,
    '\'': TokenType.SQUOTE,
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


class Parser:
    def __init__(self, inp: str):
        self.lexer = Lexer(inp)
        self.tokenizer = self.lexer.tokenize()
        self.current_token: Token = None

        self.next()

    def _next(self):
        """Get next token"""

        try:
            self.current_token = next(self.tokenizer)
        except StopIteration:
            self.current_token = Token(TokenType.EOS, '\0')

    def next(self):
        """Get next token, but skip comment"""

        self._next()

        if self.current_token.type == TokenType.PERCENT:
            self.next()
            while self.current_token.type not in [TokenType.NL, TokenType.EOS]:
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

    def parse(self) -> Database:
        return self.database()

    def database(self) -> Database:

        db = {}
        while self.current_token.type != TokenType.EOS:
            item = self.item()
            db[item.key] = item

        self.eat(TokenType.EOS)
        return Database(db)

    def item(self) -> Item:
        """Get an item:

        ```
        item := AT item_type LBRRACE key COMMA (value (COMMA value)*)? COMMA? RBRACE ;
        ```
        """

        self.skip_empty()
        self.eat(TokenType.AT)

        # get type
        item_type = ''
        while self.current_token.type == TokenType.CHAR:
            item_type += self.current_token.value
            self.next()

        # enter element
        self.skip_empty()
        self.eat(TokenType.LCBRACE)

        # get key
        item_key = ''
        while self.current_token.type == TokenType.CHAR:
            item_key += self.current_token.value
            self.next()

        self.skip_empty()
        self.eat(TokenType.COMMA)

        # get values
        values = {}
        while True:
            self.skip_empty()

            try:
                k, v = self.value()
            except ParserSyntaxError as e:
                raise ParserSyntaxError('while parsing {}, {}'.format(item_key, e))

            if k:
                values[k] = v

            self.skip_empty()
            if self.current_token.type != TokenType.COMMA:
                break
            else:
                self.next()

        self.eat(TokenType.RCBRACE)

        return Item(key=item_key, item_type=item_type, values=values)

    def value(self) -> Tuple[str, str]:
        """
        Get a value:

        ```
        value := key EQUAL str ;
        str := LBRACE CHAR* RBRACE | SQUOTE CHAR* SQUOTE | DQUOTE CHAR* DQUOTE ;
        ```

        (with `CHAR` being almost anything)
        """

        if self.current_token.type in [TokenType.COMMA, TokenType.RCBRACE]:  # empty value, skip
            return '', ''

        # get key
        key = ''
        while self.current_token.type == TokenType.CHAR:
            key += self.current_token.value
            self.next()

        # eat EQUAL
        self.skip_empty()
        self.eat(TokenType.EQUAL)
        self.skip_empty()

        # get value
        if self.current_token.type not in [TokenType.LCBRACE, TokenType.SQUOTE, TokenType.DQUOTE]:
            raise ParserSyntaxError('expected string opening while parsing {}, got {}'.format(key, self.current_token))

        opening_char = self.current_token.type
        closing_char = opening_char if opening_char != TokenType.LCBRACE else TokenType.RCBRACE
        self.next()

        value = ''
        brace_level = 1 if closing_char == TokenType.RCBRACE else 0
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
                if closing_char == TokenType.RCBRACE and brace_level == 0:
                    self.next()
                    break
            elif self.current_token.type == closing_char:
                self.next()
                break

            value += self.current_token.value
            self.next()

        return key, value