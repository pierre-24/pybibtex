from typing import Iterator, List, Tuple
from enum import Enum, unique


class Author:
    def __init__(self, first: str, last: str, von: str = None, jr: str = None):
        self.first = first
        self.last = last
        self.von = von
        self.jr = jr

    def __str__(self):
        """Return the author in the "comma" form (since it is the only one which handle "jr")
        """

        return '{}{}, {}{}'.format(
            '' if self.von is None else self.von + ' ',
            self.last,
            '' if self.jr is None else '{}, '.format(self.jr),
            self.first
        )

    def __repr__(self):
        return "Author('{}', '{}', {}, {})".format(self.first, self.last, repr(self.von), repr(self.jr))


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


class WordSequence:
    def transform(self) -> Author:
        """Transform the word sequence into an author
        """

        raise NotImplementedError()

    @staticmethod
    def to_sentence(seq: List[str], sep: str = ' ') -> str:
        return sep.join(seq)


class PureWordSequence(WordSequence):
    def __init__(self, words: List[str], capitalization: List[int]):
        self.words = words
        self.capitalizations = capitalization

    def transform(self) -> Author:
        """Transform a sequence written in "natural form" (no comma) into an author:

        1. The last word is always `last`;
        2. As long as they are uppercase or caseless, the first words are in `first`
           (stops at the first lowercase one);
        3. The remaining is in `von`;
        4. There is no `jr` part.
        """

        von = None
        jr = None
        words = self.words

        # get first
        end_first = 0
        while end_first < len(words) - 1:
            if self.capitalizations[end_first] in [1, -1]:
                end_first += 1
            else:
                break

        first = WordSequence.to_sentence(words[:end_first])

        # get last
        start_last = len(words) - 1

        while start_last > end_first:
            if self.capitalizations[start_last - 1] in [1, -1]:
                start_last -= 1
            else:
                break

        last = WordSequence.to_sentence(words[start_last:])

        # get von, if any
        if end_first != start_last:
            von = WordSequence.to_sentence(words[end_first:start_last])

        return Author(first, last, von=von, jr=jr)


class CommaSeparatedWordSequence(WordSequence):
    def __init__(self, seq: List[List[str]], capitalization: List[List[int]]):
        self.groups = seq
        self.num_fields = len(self.groups)

        self.capitalizations = capitalization

    def transform(self) -> Author:
        """Transform a sequence written in "comma form" into an author:

        1. The last group is always `first`;
        2. If they are 3 groups, the second is `jr`;
        2. Put the last word of the first group in `last`.
           Then, as long as they are uppercase or caseless, the last words of the first group
           are in `last` (stops at the first lowercase one);
        3. The remaining of the first group is in `von`;
        """

        first = WordSequence.to_sentence(self.groups[-1])
        jr = None if self.num_fields == 2 else WordSequence.to_sentence(self.groups[-2])

        words = self.groups[0]
        capitalizations = self.capitalizations[0]

        start_last = len(words) - 1

        while start_last > 0:
            if capitalizations[start_last - 1] in [1, -1]:
                start_last -= 1
            else:
                break

        last = WordSequence.to_sentence(words[start_last:])

        if start_last > 0:
            von = ' '.join(words[:start_last])
        else:
            von = None

        return Author(first, last, von=von, jr=jr)


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

    def skip_empty(self):
        """Skip spaces, newlines and comments
        """

        while self.current_token.type == AuthorTokenType.SPACE:
            self.next()

    def authors(self) -> List[Author]:
        return [s.transform() for s in self.sequences()]

    def sequences(self) -> List[WordSequence]:
        """Get a list of word sequences (either pure or comma separated) separated by "and"
        """

        sequences: List[WordSequence] = []
        words = [[]]
        capitalizations = [[]]
        group = 0

        def make_seq():
            if group == 0:
                sequences.append(PureWordSequence(words[0], capitalizations[0]))
            else:
                sequences.append(CommaSeparatedWordSequence(words, capitalizations))

        self.skip_empty()
        while self.current_token.type != AuthorTokenType.EOS:
            if self.current_token.type in [
                AuthorTokenType.LETTER, AuthorTokenType.BRACEDITEM, AuthorTokenType.SPECIALCHAR
            ]:
                word, capitalization = self.word()

                if word.lower() == 'and':
                    make_seq()
                    words = [[]]
                    capitalizations = [[]]
                else:
                    words[group].append(word)
                    capitalizations[group].append(capitalization)
                self.skip_empty()
            elif self.current_token.type == AuthorTokenType.COMMA:
                group += 1
                if group > 3:
                    raise AuthorParserSyntaxError(
                        'got {}, which is more than 2 comma!'.format(self.current_token))
                words.append([])
                capitalizations.append([])

                self.next()
                self.skip_empty()

        # catch last
        make_seq()

        return sequences

    def word(self) -> Tuple[str, int]:
        """Get a word and its capitalization,
        according to http://tug.ctan.org/info/bibtex/tamethebeast/ttb_en.pdf :
        + ``-1`` if the word is caseless,
        + ``0`` if it is lowercase,
        + ``1`` if it is uppercase

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
                if self.current_token.type == AuthorTokenType.LETTER and value.isalpha():
                    capitalization = 1 if value.upper() == value else 0
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
