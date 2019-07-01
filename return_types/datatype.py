from dataclasses import dataclass

from .literal import LiteralReturnType


@dataclass(frozen=True)
class DatatypeLiteralReturnType(LiteralReturnType):
    value: str
    type: str

    def sparql_escape(self, quote_char="'"):
        escaped_value = self.value.replace(quote_char, "\\" + quote_char)
        return f'{quote_char}{escaped_value}{quote_char}^^<{self.type}>'
