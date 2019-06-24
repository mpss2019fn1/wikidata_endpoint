from dataclasses import dataclass


@dataclass(frozen=True)
class UriReturnType:
    value: str

    def sparql_escape(self):
        return '<' + self.value + '>'
