import configparser


class WikidataEndpointConfiguration:
    DEFAULT_REMOTE_URL = "https://query.wikidata.org"
    DEFAULT_CONCURRENT_REQUESTS = 5
    DEFAULT_REQUEST_TIMEOUT = 60

    config = configparser.ConfigParser()

    def __init__(self, config_file):
        self.config.read(config_file)

    def remote_url(self):
        return self.config.get("REMOTE", "url", fallback=WikidataEndpointConfiguration.DEFAULT_REMOTE_URL)

    def concurrent_requests(self):
        return int(self.config.get("LIMITING", "concurrent_requests",
                                   fallback=WikidataEndpointConfiguration.DEFAULT_CONCURRENT_REQUESTS))

    def request_timeout(self):
        return int(self.config.get("LIMITING", "request_timeout",
                                   fallback=WikidataEndpointConfiguration.DEFAULT_REQUEST_TIMEOUT))
