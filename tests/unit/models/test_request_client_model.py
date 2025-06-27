import pytest

from src.grpy_request_client.models.request_model import RequestModel


def create_test_request_model(**kwargs):
    """Helper to create RequestModel with required fields for testing."""
    return RequestModel(**kwargs)


class TestRestClientInitialization:
    def test_init_with_defaults(self, base_url):
        client = create_test_request_model(base_url=base_url)
        assert str(client.base_url) == base_url
        assert client.method == "GET"
        assert client.endpoint == ""
        assert client.timeout == 5
        assert client.params == {}
        assert client.headers == client.DEFAULT_HEADERS

    def test_init_with_custom_values(self, base_url, endpoint):
        custom_headers = {"X-Custom-Header": "value"}
        custom_params = {"param1": "value1"}

        client = create_test_request_model(
            base_url=base_url,
            method="POST",
            endpoint=endpoint,
            timeout=30,
            params=custom_params,
            headers=custom_headers,
        )

        assert str(client.base_url) == base_url
        assert client.method == "POST"
        assert client.endpoint == endpoint
        assert client.timeout == 30
        assert client.params == custom_params
        assert isinstance(client.headers, dict)

        # Headers should be merged with defaults
        for key, value in client.DEFAULT_HEADERS.items():
            if key not in custom_headers:
                assert client.headers[key] == value
        assert client.headers["X-Custom-Header"] == "value"


class TestRequestModelValidation:
    def test_validate_http_method_valid(self, base_url, endpoint):
        for method in RequestModel.VALID_METHODS:
            client = create_test_request_model(base_url=base_url, endpoint=endpoint, method=method)
            assert client.method == method

    def test_validate_http_method_invalid(self, base_url, endpoint):
        with pytest.raises(ValueError) as excinfo:
            create_test_request_model(base_url=base_url, endpoint=endpoint, method="INVALID")
        assert "Invalid HTTP method" in str(excinfo.value)

    def test_validate_timeout_valid(self, base_url, endpoint):
        client = create_test_request_model(base_url=base_url, endpoint=endpoint, timeout=10)
        assert client.timeout == 10

        client = create_test_request_model(base_url=base_url, endpoint=endpoint, timeout=0.5)
        assert client.timeout == 0.5

    def test_validate_timeout_invalid(self, base_url, endpoint):
        with pytest.raises(ValueError) as excinfo:
            create_test_request_model(base_url=base_url, endpoint=endpoint, timeout=0)
        assert "Input should be greater than 0" in str(excinfo.value)

        with pytest.raises(ValueError):
            create_test_request_model(base_url=base_url, endpoint=endpoint, timeout=-1)
        assert "Input should be greater than 0" in str(excinfo.value)
