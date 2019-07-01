import time

import requests
import logging
import email.utils
import uuid
from datetime import datetime, timedelta, timezone

from wikidata_endpoint.return_types.datatype import DatatypeLiteralReturnType
from .return_types import LiteralReturnType, StringLiteralReturnType, UriReturnType


class URITooLongException(Exception):
    pass


class WikidataRequestExecutor:

    def __init__(self, owning_endpoint):
        self._owner = owning_endpoint
        self._on_error = None
        self._on_timeout = None
        self.response = None
        self.query = None
        self.id = uuid.uuid1()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_type, TypeError):
            self._invoke_on_error(exc_val)
        self._owner.return_executor(self)

    def get(self, query, on_error=None, on_timeout=None):
        self._set_callbacks(on_error, on_timeout)
        self.query = query
        max_query_len = self._owner.config().max_query_length()
        if len(query) > max_query_len:
            self._invoke_on_error(
                URITooLongException(f"Request URI exceeds maximum length of {max_query_len} (currently {len(query)})"))
        self._wait_while_blocked()
        try:
            self.response = requests.get(self._owner.config().remote_url(), params={"format": "json", "query": query},
                                         timeout=self._owner.config().request_timeout(),
                                         headers={"User-Agent": str(self.id)})
            return self._unpack_results()
        except requests.Timeout:
            self._invoke_on_timeout()
        return []

    def post(self, query, on_error=None, on_timeout=None):
        self._set_callbacks(on_error, on_timeout)
        self.query = query
        self._wait_while_blocked()
        try:
            self.response = requests.post(self._owner.config().remote_url(), params={"format": "json"},
                                          data={"query": query}, timeout=self._owner.config().request_timeout(),
                                          headers={"User-Agent": str(self.id)})
            return self._unpack_results()
        except requests.Timeout:
            self._invoke_on_timeout()
        return []

    def _set_callbacks(self, on_error, on_timeout):
        self._on_error = on_error
        self._on_timeout = on_timeout

    def _wait_while_blocked(self):
        if not self._owner.execution_blocked_until:
            return

        delta = self._owner.execution_blocked_until - datetime.now()
        time.sleep(max(0, delta.total_seconds()))

    @staticmethod
    def _parse_unpacked_results(query_result):
        if query_result['type'] == 'uri':
            return UriReturnType(query_result['value'])
        elif query_result['type'] == 'bnode':
            # ToDo: Handle bnode properly?
            return LiteralReturnType(query_result['value'])
        elif query_result['type'] == 'literal':
            if 'xml:lang' in query_result.keys():
                return StringLiteralReturnType(query_result['value'], query_result['xml:lang'])
            if 'datatype' in query_result.keys():
                return DatatypeLiteralReturnType(query_result['value'], query_result['datatype'])
            else:
                return LiteralReturnType(query_result['value'])
        else:
            raise Exception(f"Invalid type {query_result['type']}")

    def _unpack_results(self):
        if self.response.status_code != 200:
            self._invoke_on_error(None)
        if self._owner.config().with_return_type():
            return self._unpack_results_with_type()
        else:
            return self._unpack_results_without_type()

    def _unpack_results_without_type(self):
        try:
            for query_result in self.response.json()["results"]["bindings"]:
                yield {key: query_result[key]["value"] for key in query_result.keys()}
        except Exception as e:
            self._invoke_on_error(e)
        return []

    def _unpack_results_with_type(self):
        try:
            for query_result in self.response.json()["results"]["bindings"]:
                yield {key: self._parse_unpacked_results(query_result[key]) for key in query_result.keys()}
        except Exception as e:
            self._invoke_on_error(e)
        return []

    def _invoke_on_timeout(self):
        logging.error(f"Timeout during request against {self._owner.config().remote_url()}")
        if self._on_timeout:
            self._on_timeout(self)

    def _invoke_on_error(self, error):
        printed_error = error.__str__() if error else "No Error"
        printed_status_code = self.response.status_code if self.response else "No Response"
        logging.error(
            f"Error during request against {self._owner.config().remote_url()}: [{printed_status_code}] {printed_error}")
        if self._propagate_faulty_request() and self._on_error:
            self._on_error(self, error)

    def _propagate_faulty_request(self):
        if not self.response:
            return True

        if self.response.status_code == 429:
            self._owner.execution_blocked_until = WikidataRequestExecutor._parse_http_retry(
                self.response.headers["Retry-After"])
            logging.warning(f"Rate limit exceeded. Blocked until {self._owner.execution_blocked_until}")
            return False

        if self.response.status_code == 500:
            if "java.util.concurrent.TimeoutException" in self.response.content:
                self._invoke_on_timeout()
                return False

        return True

    @staticmethod
    def _parse_http_retry(retry_header):
        if not retry_header:
            return None
        gmt_timestamp = email.utils.parsedate_to_datetime(retry_header)
        if not gmt_timestamp:
            return datetime.now() + timedelta(seconds=int(retry_header))

        return gmt_timestamp.astimezone(datetime.now(timezone.utc).astimezone().tzinfo)
