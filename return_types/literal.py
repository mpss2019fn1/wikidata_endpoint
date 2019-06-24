from dataclasses import dataclass


@dataclass
class LiteralReturnType:
    value: str

    def sparql_escape(self):
        return self.value
