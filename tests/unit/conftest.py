from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from aiohttp import ClientResponse, ClientSession

from src.grpy_request_client.models.request_model import RequestModel


@pytest.fixture
def base_url():
    return "https://api.example.com/"


@pytest.fixture
def endpoint():
    return "v1/resource"


@pytest.fixture
def request_data(base_url):
    return RequestModel(base_url=base_url)


@pytest.fixture
def mock_client_session():
    def _create_session(response=None, side_effect=None):
        mock_session = MagicMock(spec=ClientSession)
        mock_session.closed = False

        # Mock the close method
        async def mock_close():
            mock_session.closed = True

        mock_session.close = mock_close

        # Mock the request method
        if side_effect:
            mock_session.request = AsyncMock(side_effect=side_effect)
        else:
            mock_session.request = AsyncMock(return_value=response)

        # Make session work as an async context manager
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        return mock_session

    return _create_session


@pytest.fixture
def mock_session():
    """
    Fixture that provides a mock ClientSession.

    By default, the session's request method returns a 200 OK response.
    The response can be customized by setting session.request.return_value.
    """
    session = Mock(spec=ClientSession)
    session.request = AsyncMock()
    return session


@pytest.fixture
def mock_session_factory(mock_client_response):
    """
    Fixture that provides a factory for creating mock sessions with preconfigured responses.

    Returns a function that creates a mock session with a response of the specified status.
    """

    def _create_session(status=200, reason="OK", **response_kwargs):
        mock_response = mock_client_response(status=status, reason=reason, **response_kwargs)
        session = Mock(spec=ClientSession)
        session.request = AsyncMock(return_value=mock_response)
        return session, mock_response

    return _create_session


@pytest.fixture
def mock_client_response():
    """
    Fixture that provides a configurable mock ClientResponse.

    Returns a factory function that creates mock responses with specified attributes.
    """

    def _create_response(
        status=200, reason="OK", headers=None, request_info=None, history=None, content=None
    ):
        mock_response = Mock(spec=ClientResponse)
        mock_response.status = status
        mock_response.reason = reason
        mock_response.headers = headers or {}
        mock_response.request_info = request_info or Mock()
        mock_response.history = history or []

        # For content handling
        if content is not None:

            async def mock_text():
                return content if isinstance(content, str) else str(content)

            async def mock_json():
                return content if not isinstance(content, str) else None

            mock_response.text = mock_text
            mock_response.json = mock_json

        return mock_response

    return _create_response
