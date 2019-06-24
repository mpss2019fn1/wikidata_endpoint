from wikidata_request_executor import WikidataRequestExecutor
from wikidata_endpoint_configuration import WikidataEndpointConfiguration
from wikidata_endpoint import WikidataEndpoint
from pathlib import Path
from pytest import fixture


def endpoint_configuration():
    return WikidataEndpointConfiguration(Path("tests/test_config.ini"))


@fixture
def endpoint():
    return WikidataEndpoint(endpoint_configuration())


@fixture
def endpoint_result():
    return open('tests/test_result.json').read()


def test_get_method(requests_mock, endpoint, endpoint_result):
    requests_mock.get(endpoint.config().remote_url(), text=endpoint_result)
    executor = WikidataRequestExecutor(endpoint)
    result = list(executor.get('query'))
    assert len(result) == 1
    assert set(result[0].keys()) == {'a', 'b', 'c'}
    assert result[0]['a'] == 'http://test.example'
    assert result[0]['b'] == 'Test'
    assert result[0]['c'] == '42'


def test_post_method(requests_mock, endpoint, endpoint_result):
    requests_mock.post(endpoint.config().remote_url(), text=endpoint_result)
    executor = WikidataRequestExecutor(endpoint)
    result = list(executor.post('query'))
    assert len(result) == 1
    assert set(result[0].keys()) == {'a', 'b', 'c'}
    assert result[0]['a'] == 'http://test.example'
    assert result[0]['b'] == 'Test'
    assert result[0]['c'] == '42'
