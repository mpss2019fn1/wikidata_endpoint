from dataclasses import dataclass


@dataclass(frozen=True)
class LiteralReturnType:
    value: str

    def sparql_escape(self, quote_char="'"):
        return quote_char + self.value.replace(quote_char, '\\' + quote_char) + quote_char
