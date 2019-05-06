import time

import requests
import logging
import email.utils
from datetime import datetime, timedelta, timezone


class URITooLongException(Exception):
    pass


class WikidataRequestExecutor:

    def __init__(self, owning_endpoint):
        self._owner = owning_endpoint
        self._on_error = None
        self._on_timeout = None
        self.response = None
        self.query = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_type, TypeError):
            self._invoke_on_error(exc_val)
        self._owner.return_executor(self)

    def get(self, query, on_error=None, on_timeout=None):
        self._set_callbacks(on_error, on_timeout)
        self.query = query
        if len(query) > 2048:
            self._invoke_on_error(URITooLongException())
        self._wait_while_blocked()
        try:
            self.response = requests.get(self._owner.config().remote_url(), params={"format": "json", "query": query})
            yield self._unpack_results()
        except requests.Timeout:
            self._invoke_on_timeout()

    def post(self, query, on_error=None, on_timeout=None):
        self._set_callbacks(on_error, on_timeout)
        self.query = query
        self._wait_while_blocked()
        try:
            self.response = requests.post(self._owner.config().remote_url(), params={"format": "json"},
                                          data={"query": query})
            yield self._unpack_results()
        except requests.Timeout:
            self._invoke_on_timeout()

    def _set_callbacks(self, on_error, on_timeout):
        self._on_error = on_error
        self._on_timeout = on_timeout

    def _unpack_results(self):
        if self.response.status_code != 200:
            self._invoke_on_error(None)
        try:
            for query_result in self.response.json()["results"]["bindings"]:
                yield {key: query_result[key]["value"] for key in query_result.keys()}
        except Exception as e:
            self._invoke_on_error(e)

    def _invoke_on_timeout(self):
        logging.error(f"Timeout during request against {self._owner.config().remote_url()}")
        if self._on_timeout:
            self._on_timeout(self)

    def _invoke_on_error(self, error):
        logging.error(f"Error during request against {self._owner.config().remote_url()}", error)
        if self.response and self.response.status_code == 429:
            self._owner.execution_blocked_until = WikidataRequestExecutor._parse_http_retry(
                self.response.headers["Retry-After"])
            logging.warning(f"[429] Request got rejected. Blocked until {self._owner.execution_blocked_until}")

        if self._on_error:
            self._on_error(self, error)

    @staticmethod
    def _parse_http_retry(retry_header):
        if not retry_header:
            return None
        gmt_timestamp = email.utils.parsedate_to_datetime(retry_header)
        if not gmt_timestamp:
            return datetime.now() + timedelta(seconds=int(retry_header))

        return gmt_timestamp.astimezone(datetime.now(timezone.utc).astimezone().tzinfo)

    def _wait_while_blocked(self):
        if not self._owner.execution_blocked_until:
            return

        delta = self._owner.execution_blocked_until - datetime.now()
        time.sleep(max(0, delta.total_seconds()))
