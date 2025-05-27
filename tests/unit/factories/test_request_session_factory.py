from unittest.mock import MagicMock, patch

import pytest
from aiohttp import ClientSession

from request.factories.request_session_factory import RequestSessionFactory


class TestRequestSessionFactory:
    """Tests for the RequestSessionFactory class."""

    @pytest.fixture(autouse=True)
    async def cleanup(self):
        """Clean up any sessions after each test."""
        yield
        await RequestSessionFactory.close_session()
        # Reset the singleton state
        RequestSessionFactory._session = None

    def test_singleton_pattern(self):
        """Test that RequestSessionFactory implements the singleton pattern."""
        factory1 = RequestSessionFactory()
        factory2 = RequestSessionFactory()

        # Both instances should be the same object
        assert factory1 is factory2

    @pytest.mark.asyncio
    async def test_create_session(self):
        """Test creating a new session with default parameters."""
        with (
            patch("request.factories.request_session_factory.ClientSession") as mock_session,
            patch("request.factories.request_session_factory.TCPConnector") as mock_connector,
            patch("request.factories.request_session_factory.ClientTimeout") as mock_timeout,
        ):
            # Setup mocks
            mock_session_instance = MagicMock(spec=ClientSession)
            mock_session.return_value = mock_session_instance

            # Call the method
            session = RequestSessionFactory.create_session()

            # Verify session was created with expected parameters
            mock_connector.assert_called_once_with()
            mock_timeout.assert_called_once_with(total=30)
            mock_session.assert_called_once()
            assert session == mock_session_instance

    @pytest.mark.asyncio
    async def test_create_session_with_custom_timeout(self):
        """Test creating a session with custom timeout."""
        with (
            patch("request.factories.request_session_factory.ClientSession") as mock_session,
            patch("request.factories.request_session_factory.TCPConnector") as mock_connector,
            patch("request.factories.request_session_factory.ClientTimeout") as mock_timeout,
        ):
            # Setup mocks
            mock_session_instance = MagicMock(spec=ClientSession)
            mock_session.return_value = mock_session_instance

            # Call the method with custom timeout
            session = RequestSessionFactory.create_session(timeout=60)

            # Verify timeout was created with expected value
            mock_connector.assert_called_once_with()
            mock_timeout.assert_called_once_with(total=60)
            mock_session.assert_called_once()
            assert session == mock_session_instance

    @pytest.mark.asyncio
    async def test_create_session_with_connector_options(self):
        """Test creating a session with custom connector options."""
        with (
            patch("request.factories.request_session_factory.ClientSession") as mock_session,
            patch("request.factories.request_session_factory.TCPConnector") as mock_connector,
            patch("request.factories.request_session_factory.ClientTimeout") as mock_timeout,
        ):
            # Setup mocks
            mock_session_instance = MagicMock(spec=ClientSession)
            mock_session.return_value = mock_session_instance

            # Call the method with connector options
            connector_options = {"limit": 20, "ssl": False}
            session = RequestSessionFactory.create_session(connector_options=connector_options)

            # Verify connector was created with expected options
            mock_connector.assert_called_once_with(**connector_options)
            mock_timeout.assert_called_once_with(total=30)
            mock_session.assert_called_once()
            assert session == mock_session_instance

    @pytest.mark.asyncio
    async def test_get_session_creates_new_if_none_exists(self):
        """Test that get_session creates a new session if none exists."""
        # Reset the singleton state
        RequestSessionFactory._session = None

        with patch.object(RequestSessionFactory, "create_session") as mock_create:
            mock_session = MagicMock(spec=ClientSession)
            mock_session.closed = False
            mock_create.return_value = mock_session

            # Call get_session
            session = RequestSessionFactory.get_session()

            # Verify create_session was called and returned session is correct
            mock_create.assert_called_once()
            assert session == mock_session
            assert RequestSessionFactory._session == mock_session

    @pytest.mark.asyncio
    async def test_get_session_returns_existing_session(self):
        """Test that get_session returns existing session if available."""
        # Setup existing session
        mock_session = MagicMock(spec=ClientSession)
        mock_session.closed = False
        RequestSessionFactory._session = mock_session

        with patch.object(RequestSessionFactory, "create_session") as mock_create:
            # Call get_session
            session = RequestSessionFactory.get_session()

            # Verify create_session was not called and existing session is returned
            mock_create.assert_not_called()
            assert session == mock_session

    @pytest.mark.asyncio
    async def test_get_session_creates_new_if_existing_closed(self):
        """Test that get_session creates a new session if existing one is closed."""
        # Setup closed session
        mock_closed_session = MagicMock(spec=ClientSession)
        mock_closed_session.closed = True
        RequestSessionFactory._session = mock_closed_session

        with patch.object(RequestSessionFactory, "create_session") as mock_create:
            mock_new_session = MagicMock(spec=ClientSession)
            mock_new_session.closed = False
            mock_create.return_value = mock_new_session

            # Call get_session
            session = RequestSessionFactory.get_session()

            # Verify create_session was called and new session is returned
            mock_create.assert_called_once()
            assert session == mock_new_session
            assert RequestSessionFactory._session == mock_new_session

    @pytest.mark.asyncio
    async def test_close_session(self):
        """Test closing the shared session."""
        # Setup mock session
        mock_session = MagicMock(spec=ClientSession)
        mock_session.closed = False
        RequestSessionFactory._session = mock_session

        # Call close_session
        await RequestSessionFactory.close_session()

        # Verify session was closed
        mock_session.close.assert_called_once()
        assert RequestSessionFactory._session is None

    @pytest.mark.asyncio
    async def test_close_session_with_no_session(self):
        """Test closing when no session exists."""
        # Ensure no session exists
        RequestSessionFactory._session = None

        # This should not raise any errors
        await RequestSessionFactory.close_session()
