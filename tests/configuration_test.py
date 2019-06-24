from pathlib import Path

from wikidata_endpoint.wikidata_endpoint_configuration import WikidataEndpointConfiguration

from pytest import fixture


@fixture
def endpoint_configuration():
    return WikidataEndpointConfiguration(Path("tests/test_config.ini"))


def test_value_reading(endpoint_configuration):
    assert endpoint_configuration.remote_url() == 'http://test-url.com'
    assert endpoint_configuration.concurrent_requests() == 42
    assert endpoint_configuration.request_timeout() == 43
    assert endpoint_configuration.with_return_type() == 0
