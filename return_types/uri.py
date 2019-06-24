from dataclasses import dataclass


@dataclass
class UriReturnType:
    value: str

    def sparql_escape(self):
        return '<' + self.value + '>'
