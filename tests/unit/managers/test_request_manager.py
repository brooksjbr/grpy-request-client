from asyncio import TimeoutError
from unittest.mock import AsyncMock, Mock

import pytest
from aiohttp import (
    ClientConnectorError,
    ClientConnectorSSLError,
    ClientResponseError,
    ClientSession,
    ServerDisconnectedError,
)

from src.grpy_request_client.managers.request_manager import RequestManager


class TestRequestManager:
    """Tests for the RequestManager class."""

    def test_init_without_session(self, request_data):
        """Test initialization of RequestManager without session."""
        # Initialize RequestManager without session
        http_request = RequestManager(requestData=request_data)

        # Verify the request data was properly set
        assert http_request.requestData == request_data
        # Verify session is None and we own the session
        assert http_request.session is None
        assert http_request._owns_session is True

    def test_init_with_session(self, request_data, mock_client_session):
        """Test initialization of RequestManager with session."""
        # Initialize RequestManager with the mock request data and session
        http_request = RequestManager(requestData=request_data, session=mock_client_session)

        # Verify the request data and session were properly set
        assert http_request.requestData == request_data
        assert http_request.session == mock_client_session
        assert http_request._owns_session is False

    @pytest.mark.asyncio
    async def test_async_context_manager_without_session(self, request_data):
        """Test that RequestManager works as an async context manager without session."""
        # Use RequestManager as an async context manager without session
        async with RequestManager(requestData=request_data) as http_request:
            # Verify the instance is returned by __aenter__
            assert isinstance(http_request, RequestManager)
            assert http_request.requestData == request_data
            # Verify session was created
            assert http_request.session is not None
            assert isinstance(http_request.session, ClientSession)
            assert http_request._owns_session is True

        # Verify session is cleaned up after exit
        assert http_request.session is None

    @pytest.mark.asyncio
    async def test_async_context_manager_with_session(self, request_data, mock_client_session):
        """Test that RequestManager works as an async context manager with a session."""
        # Use RequestManager as an async context manager with a session
        async with RequestManager(
            requestData=request_data, session=mock_client_session
        ) as http_request:
            # Verify the instance is returned by __aenter__
            assert isinstance(http_request, RequestManager)
            assert http_request.requestData == request_data
            # Verify the session is properly set
            assert http_request.session == mock_client_session
            assert http_request._owns_session is False

        # External session should still be available
        assert http_request.session == mock_client_session

    @pytest.mark.asyncio
    async def test_ensure_session_without_session_raises_error(self, request_data):
        """Test that _ensure_session raises error when no session is available."""
        http_request = RequestManager(requestData=request_data)

        with pytest.raises(RuntimeError, match="No session available"):
            await http_request._ensure_session()

    @pytest.mark.asyncio
    async def test_ensure_session_with_session_returns_session(
        self, request_data, mock_client_session
    ):
        """Test that _ensure_session returns session when available."""
        http_request = RequestManager(requestData=request_data, session=mock_client_session)

        session = await http_request._ensure_session()
        assert session == mock_client_session

    @pytest.mark.asyncio
    async def test_execute_request_without_session_outside_context(self, request_data):
        """Test executing request without session outside context manager raises error."""
        http_request = RequestManager(requestData=request_data)

        with pytest.raises(RuntimeError, match="No session available"):
            await http_request.execute_request()

    @pytest.mark.asyncio
    async def test_execute_request_get(self, request_data, mock_session_factory):
        """Test executing a GET request."""
        # Create a mock session with a 200 OK response
        mock_session, mock_response = mock_session_factory(status=200)

        # Create the RequestManager instance
        http_request = RequestManager(requestData=request_data, session=mock_session)

        # Execute the request
        response = await http_request.execute_request()

        # Verify the response is the mock response
        assert response == mock_response

        # Verify the session's request method was called with the correct arguments
        mock_session.request.assert_called_once_with(
            method=request_data.method,
            url=str(request_data.base_url) + request_data.endpoint,
            params=request_data.params,
            headers=request_data.headers,
            timeout=request_data.timeout,
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status_code,reason,error_type",
        [
            # 4XX Client Errors
            (400, "Bad Request", "Client error"),
            (401, "Unauthorized", "Client error"),
            (403, "Forbidden", "Client error"),
            (404, "Not Found", "Client error"),
            (429, "Too Many Requests", "Client error"),
            # 5XX Server Errors
            (500, "Internal Server Error", "Server error"),
            (502, "Bad Gateway", "Server error"),
            (503, "Service Unavailable", "Server error"),
            (504, "Gateway Timeout", "Server error"),
        ],
    )
    async def test_execute_request_error_responses(
        self, request_data, mock_session_factory, status_code, reason, error_type
    ):
        """Test executing requests that return error status codes (4xx and 5xx)."""
        # Create a mock session with the specified error response
        mock_session, _ = mock_session_factory(status=status_code, reason=reason)

        # Create the RequestManager instance
        http_request = RequestManager(requestData=request_data, session=mock_session)

        # Execute the request and expect a ClientResponseError
        with pytest.raises(ClientResponseError) as excinfo:
            await http_request.execute_request()

        # Verify the exception has the correct status and message
        assert excinfo.value.status == status_code
        assert reason in str(excinfo.value)

        # Verify the error type is correctly identified in the exception message
        if error_type == "Client error":
            assert status_code >= 400 and status_code < 500
        else:  # Server error
            assert status_code >= 500 and status_code < 600

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "exception_class,exception_args,expected_exception_type",
        [
            (ClientConnectorError, [Mock(), OSError("Connection refused")], ClientConnectorError),
            (ClientConnectorSSLError, [Mock(), OSError("SSL error")], ClientConnectorSSLError),
            (ServerDisconnectedError, ["Server disconnected"], ServerDisconnectedError),
            (TimeoutError, [], TimeoutError),
        ],
    )
    async def test_execute_request_network_errors(
        self, request_data, mock_session, exception_class, exception_args, expected_exception_type
    ):
        """Test handling of network and connection errors."""
        # Configure the mock session to raise the specified exception
        exception = exception_class(*exception_args)
        mock_session.request = AsyncMock(side_effect=exception)

        # Create the RequestManager instance
        http_request = RequestManager(requestData=request_data, session=mock_session)

        # Execute the request and expect the appropriate exception
        with pytest.raises(expected_exception_type):
            await http_request.execute_request()

        # Verify the session's request method was called with the correct arguments
        mock_session.request.assert_called_once_with(
            method=request_data.method,
            url=f"{request_data.base_url}{request_data.endpoint}",
            params=request_data.params,
            headers=request_data.headers,
            timeout=request_data.timeout,
        )

    @pytest.mark.asyncio
    async def test_execute_request_general_exception(self, request_data, mock_session):
        """Test handling of general exceptions during request execution."""
        # Configure the mock session to raise a general exception
        mock_session.request = AsyncMock(side_effect=Exception("Unexpected error"))

        # Create the RequestManager instance
        http_request = RequestManager(requestData=request_data, session=mock_session)

        # Execute the request and expect the exception to be re-raised
        with pytest.raises(Exception) as excinfo:
            await http_request.execute_request()

        # Verify the exception contains the expected message
        assert "Unexpected error" in str(excinfo.value)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status_code,reason,expected_message",
        [
            (401, "Unauthorized", "Authentication failed"),
            (403, "Forbidden", "Authorization failed"),
        ],
    )
    async def test_execute_request_auth_errors(
        self, request_data, mock_session_factory, status_code, reason, expected_message
    ):
        """Test handling of authentication and authorization errors."""
        # Create a mock session with the specified error response
        mock_session, mock_response = mock_session_factory(status=status_code, reason=reason)

        # Create the RequestManager instance
        http_request = RequestManager(requestData=request_data, session=mock_session)

        # Execute the request and expect a ClientResponseError
        with pytest.raises(ClientResponseError) as excinfo:
            await http_request.execute_request()

        # Verify the exception has the correct status and message
        assert excinfo.value.status == status_code
        assert expected_message in str(excinfo.value)
        assert reason in str(excinfo.value)
