import configparser


class WikidataEndpointConfiguration:
    DEFAULT_REMOTE_URL = "https://query.wikidata.org"
    DEFAULT_CONCURRENT_REQUESTS = 5
    DEFAULT_REQUEST_TIMEOUT = 60
    DEFAULT_WITH_RETURN_TYPE = False

    config = configparser.ConfigParser()

    def __init__(self, config_file):
        self.config.read(config_file)

    def remote_url(self):
        return self.config.get("REMOTE", "url", fallback=self.DEFAULT_REMOTE_URL)

    def concurrent_requests(self):
        return int(self.config.get("LIMITING", "concurrent_requests", fallback=self.DEFAULT_CONCURRENT_REQUESTS))

    def request_timeout(self):
        return int(self.config.get("LIMITING", "request_timeout", fallback=self.DEFAULT_REQUEST_TIMEOUT))

    def with_return_type(self):
        return int(self.config.get("OTHER", "with_return_type", fallback=self.DEFAULT_WITH_RETURN_TYPE))
