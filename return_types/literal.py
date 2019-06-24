from dataclasses import dataclass


@dataclass(frozen=True)
class LiteralReturnType:
    value: str

    def sparql_escape(self):
        return self.value
