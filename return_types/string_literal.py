from dataclasses import dataclass

from return_types.literal import LiteralReturnType


@dataclass
class StringLiteralReturnType(LiteralReturnType):
    value: str
    language: str

    def sparql_escape(self):
        return self.value + '@' + self.language
