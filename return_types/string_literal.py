from dataclasses import dataclass

from .literal import LiteralReturnType


@dataclass(frozen=True)
class StringLiteralReturnType(LiteralReturnType):
    value: str
    language: str

    def sparql_escape(self, quote_char="'"):
        return super().sparql_escape(quote_char) + '@' + self.language
