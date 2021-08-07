from typing import Iterator, List, Tuple
from enum import Enum, unique


class Author:
    def __init__(self, first: str, last: str, von: str = None, jr: str = None):
        self.first = first
        self.last = last
        self.von = von
        self.jr = jr

    def __str__(self):
        return '{}{}, {}{}'.format(
            '' if self.von is None else self.von + ' ',
            self.last,
            '' if self.jr is None else '{}, '.format(self.jr),
            self.first
        )


@unique
class AuthorTokenType(Enum):
    COMMA = ','
    LETTER = 'LET'
    BRACEDITEM = 'ITM'
    SPECIALCHAR = 'SCH'
    SPACE = 'SPC'
    EOS = '\0'


AUTHOR_SYMBOL_TR = {
    ',': AuthorTokenType.COMMA,
    ' ': AuthorTokenType.SPACE
}


class AuthorToken:
    def __init__(self, typ_: AuthorTokenType, value: str, position: int = -1):
        self.type = typ_
        self.value = value
        self.position = position

    def __repr__(self):
        return "Token({}, '{}'{})".format(
            self.type,
            self.value,
            '' if self.position < 0 else ', {}'.format(self.position)
        )


class AuthorParserSyntaxError(Exception):
    pass


class AuthorsParser:
    """Parser to extract the authors
    """

    def __init__(self, inp):
        self.input = inp
        self.current_token: AuthorToken = None
        self.tokenizer = self.tokenize()

        self.next()

    def next(self):
        """Go to next token
        """

        try:
            self.current_token = next(self.tokenizer)
        except StopIteration:
            self.current_token = AuthorToken(AuthorTokenType.EOS, '\0')

    def eat(self, typ: AuthorTokenType):
        if self.current_token.type == typ:
            self.next()
        else:
            raise AuthorParserSyntaxError('expected {}, got {}'.format(typ, self.current_token))

    def tokenize(self) -> Iterator[AuthorToken]:
        i = 0
        while i < len(self.input):
            current_char = self.input[i]
            if current_char in AUTHOR_SYMBOL_TR:
                yield AuthorToken(AUTHOR_SYMBOL_TR[current_char], current_char, i)
            elif current_char == '{':
                j = i + 1
                is_special = False
                opening_level = 1
                while j < len(self.input):
                    cc = self.input[j]
                    if j == i + 1 and cc == '\\':
                        is_special = True
                    if cc == '{':
                        opening_level += 1
                    elif cc == '}':
                        opening_level -= 1
                        if opening_level == 0:
                            break
                    j += 1
                if opening_level != 0:
                    raise AuthorParserSyntaxError('unmatched braces while EOS!')
                else:
                    yield AuthorToken(
                        AuthorTokenType.BRACEDITEM if not is_special else AuthorTokenType.SPECIALCHAR,
                        self.input[i:j + 1],
                        i)
                    i = j
            else:
                yield AuthorToken(AuthorTokenType.LETTER, current_char, i)

            i += 1

        yield AuthorToken(AuthorTokenType.EOS, '\0', i)

    def authors(self) -> List[Author]:
        authors = []

        while self.current_token.type != AuthorTokenType.EOS:
            authors.append(self.author())

        return authors

    @staticmethod
    def get_capitalization(word: str):
        """Get the capitalization of the word according to
        http://artis.imag.fr/~Xavier.Decoret/resources/xdkbibtex/bibtex_summary.html#case_determination
        """

        pass

    def author(self) -> Author:
        words = []
        capitalizations = []
        pos_comma = []

        while self.current_token.type != AuthorTokenType.EOS:
            if self.current_token.type in [
                AuthorTokenType.LETTER, AuthorTokenType.BRACEDITEM, AuthorTokenType.SPECIALCHAR
            ]:
                w, c = self.word()
                if w.lower() == 'and':
                    self.next()
                    break
                words.append(w)
                capitalizations.append(c)
            elif self.current_token.type == AuthorTokenType.COMMA:
                pos_comma.append(len(words))
                self.next()
            else:
                self.next()

        print(words, pos_comma, capitalizations)

    def word(self) -> Tuple[str, int]:
        """Get a word and its capitalization,
        according to http://tug.ctan.org/info/bibtex/tamethebeast/ttb_en.pdf :
        + ``-1`` if the word is caseless,
        + ``0`` if it is lowercase,
        + ``1`` if it is upercase

        Note: a BRACEDITEM has no case, but a special character has the one of its argument
        """

        check_capitalization = True
        capitalization = -1
        word = ''
        while self.current_token.type in [
            AuthorTokenType.LETTER, AuthorTokenType.BRACEDITEM, AuthorTokenType.SPECIALCHAR
        ]:
            value = self.current_token.value
            if check_capitalization:
                if self.current_token.type == AuthorTokenType.LETTER:
                    if value.isalpha():
                        capitalization = 1 if value.upper() == value else 0
                        check_capitalization = False
                    elif value.isdigit():
                        capitalization = 0
                        check_capitalization = False
                elif self.current_token.type == AuthorTokenType.SPECIALCHAR:
                    # quick and dirty look for argument
                    i = 2

                    # skip command name
                    if value[i].isalpha():
                        while i < len(value) and value[i].isalpha():
                            i += 1

                    # take next alpha (should be the argument)
                    while i < len(value) and not value[i].isalnum():
                        i += 1

                    if i < len(value):
                        capitalization = 1 if value[i].upper() == value[i] else 0
                        check_capitalization = False

            word += value
            self.next()

        return word, capitalization
