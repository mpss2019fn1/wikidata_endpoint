from dataclasses import dataclass


@dataclass(frozen=True)
class UriReturnType:
    value: str

    def sparql_escape(self):
        if self.value.startswith('http://www.wikidata.org/entity/P'):
            return 'wdt:P' + self.value.split('http://www.wikidata.org/entity/P')[-1]
        return '<' + self.value + '>'
