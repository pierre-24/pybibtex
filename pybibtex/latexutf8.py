from typing import Iterator
from enum import Enum, unique

from pybibtex._utf8translate import TRANSLATION_TABLE, REVERSE_TRANSLATION_TABLE


def utf8decode(inp) -> str:
    """Replace declared UTF-8 character by their LaTeX equivalent
    """
    return inp.translate(TRANSLATION_TABLE)


@unique
class LtxTokenType(Enum):
    LCBRACE = '{'
    RCBRACE = '}'
    SPACE = 'SPC'
    ALPHA = 'ALH'
    CHAR = 'CHR'
    BACKSLASH = '\\'
    EOS = '\0'


LTX_SYMBOL_TR = {
    '{': LtxTokenType.LCBRACE,
    '}': LtxTokenType.RCBRACE,
    ' ': LtxTokenType.SPACE,
    '\\': LtxTokenType.BACKSLASH
}


class LtxToken:
    def __init__(self, typ_: LtxTokenType, value: str, position: int = -1):
        self.type = typ_
        self.value = value
        self.position = position

    def __repr__(self):
        return "Token({}, '{}'{})".format(
            self.type,
            self.value,
            '' if self.position < 0 else ', {}'.format(self.position)
        )


class LtxParserSyntaxError(Exception):
    pass


class LtxUTF8Parser:
    """Micro LaTeX parser for the macro with an UTF-8 equivalent
    """

    def __init__(self, inp, macro_def: dict):
        self.input = inp
        self.current_token: LtxToken = None
        self.tokenizer = self.tokenize()
        self.macro_def = macro_def

        self.next()

    def next(self):
        """Go to next token
        """

        try:
            self.current_token = next(self.tokenizer)
        except StopIteration:
            self.current_token = LtxToken(LtxTokenType.EOS, '\0')

    def eat(self, typ: LtxTokenType):
        if self.current_token.type == typ:
            self.next()
        else:
            raise LtxParserSyntaxError('expected {}, got {}'.format(typ, self.current_token))

    def tokenize(self) -> Iterator[LtxToken]:
        i = 0
        while i < len(self.input):
            current_char = self.input[i]
            if current_char in LTX_SYMBOL_TR:
                yield LtxToken(LTX_SYMBOL_TR[current_char], current_char, i)
            elif current_char.isalpha():
                yield LtxToken(LtxTokenType.ALPHA, current_char, i)
            else:
                yield LtxToken(LtxTokenType.CHAR, current_char, i)
            i += 1

        yield LtxToken(LtxTokenType.EOS, '\0', i)

    def transform(self) -> str:
        ret = ''
        while self.current_token.type != LtxTokenType.EOS:
            if self.current_token.type == LtxTokenType.BACKSLASH:
                prev_was_lcbrace = len(ret) > 0 and ret[-1] == LtxTokenType.LCBRACE.value
                value = self.macro()

                # remove enclosing braces if the replacement actually happened:
                if prev_was_lcbrace and value[0] != '\\' and self.current_token.type == LtxTokenType.RCBRACE:
                    self.eat(LtxTokenType.RCBRACE)
                    ret = ret[:-1]

                ret += value
            else:
                ret += self.plain_text()

        return ret

    def plain_text(self) -> str:
        """Get a portion of plain text"""
        ret = ''
        while self.current_token.type not in [LtxTokenType.BACKSLASH, LtxTokenType.EOS]:
            ret += self.current_token.value
            self.next()

        return ret

    def macro(self, skip_arg: bool = False) -> str:
        """Get a macro, return its value if defined, left as is if not
        """
        self.eat(LtxTokenType.BACKSLASH)

        # get macro name
        name = ''
        is_alpha_name = False
        if self.current_token.type == LtxTokenType.CHAR:
            name = self.current_token.value
            self.next()
        elif self.current_token.type == LtxTokenType.ALPHA:
            is_alpha_name = True
            while self.current_token.type == LtxTokenType.ALPHA:
                name += self.current_token.value
                self.next()

        if skip_arg or name not in self.macro_def:  # not a defined macro, skip
            return '\\{}'.format(name)

        macro_val = self.macro_def[name]

        if type(macro_val) is int:  # no argument
            return chr(macro_val)
        else:  # argument
            no_arg = ''
            if self.current_token.type == LtxTokenType.BACKSLASH:
                arg = self.macro(skip_arg=True)
                no_arg = '\\{}'.format(arg)
            elif self.current_token.type == LtxTokenType.LCBRACE:
                arg = self.enclosed_arg()
                no_arg = '{{{}}}'.format(arg)
            else:
                if is_alpha_name:
                    self.eat(LtxTokenType.SPACE)
                    no_arg = ' '
                arg = self.current_token.value
                no_arg += arg
                self.next()

            if arg in macro_val:
                return chr(macro_val[arg])
            else:
                return '\\{}{}'.format(name, no_arg)

    def enclosed_arg(self) -> str:
        """Get enclosed content (for macro arg), inside a pair of ``LCBRACE`` and ``RCBRACE``
        """

        self.eat(LtxTokenType.LCBRACE)
        opening_level = 1
        out = ''

        while True:
            if self.current_token.type == LtxTokenType.EOS:
                raise LtxParserSyntaxError('got {} while parsing string'.format(self.current_token))
            elif self.current_token.type == LtxTokenType.LCBRACE:
                opening_level += 1
            elif self.current_token.type == LtxTokenType.RCBRACE:
                opening_level -= 1
                if opening_level == 0:
                    break

            out += self.current_token.value
            self.next()

        self.eat(LtxTokenType.RCBRACE)
        return out


def utf8encode(inp) -> str:
    """Replace LaTeX characters by their UTF-8 equivalent
    """

    return LtxUTF8Parser(inp, REVERSE_TRANSLATION_TABLE).transform()
