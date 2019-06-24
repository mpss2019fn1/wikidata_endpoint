from dataclasses import dataclass

from .literal import LiteralReturnType


@dataclass(frozen=True)
class StringLiteralReturnType(LiteralReturnType):
    value: str
    language: str

    def sparql_escape(self, quote_char="'"):
        return quote_char + self.value.replace(quote_char, '\\' + quote_char) + quote_char + '@' + self.language
