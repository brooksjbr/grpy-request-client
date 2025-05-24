import pytest

from src.grpy.models.request_model import RequestModel


@pytest.fixture
def base_url():
    return "https://api.example.com"


@pytest.fixture
def endpoint():
    return "/v1/resource"


@pytest.fixture
def request_data(base_url):
    return RequestModel(base_url=base_url)
