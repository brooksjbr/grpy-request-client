from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientSession

from src.grpy_request_client.managers.session_manager import SessionManager


class TestSessionManager:
    """Tests for the SessionManager class."""

    @pytest.fixture(autouse=True)
    async def cleanup(self):
        """Clean up any sessions after each test."""
        yield
        # Only close if there's a real session, not a mock
        if (
            hasattr(SessionManager, "_shared_session")
            and SessionManager._shared_session is not None
            and not isinstance(SessionManager._shared_session, MagicMock)
        ):
            await SessionManager.close_shared_session()
        # Reset the singleton state
        SessionManager._shared_session = None

    def test_singleton_pattern(self):
        """Test that SessionManager implements the singleton pattern."""
        factory1 = SessionManager()
        factory2 = SessionManager()

        # Both instances should be the same object
        assert factory1 is factory2

    @pytest.mark.asyncio
    async def test_create_session(self):
        """Test creating a new session with default parameters."""
        with (
            patch("src.grpy_request_client.managers.session_manager.ClientSession") as mock_session,
            patch(
                "src.grpy_request_client.managers.session_manager.TCPConnector"
            ) as mock_connector,
            patch("src.grpy_request_client.managers.session_manager.ClientTimeout") as mock_timeout,
        ):
            # Setup mocks
            mock_session_instance = MagicMock(spec=ClientSession)
            mock_session.return_value = mock_session_instance

            # Call the method
            session = SessionManager.create_session()

            # Verify session was created with expected parameters
            mock_connector.assert_called_once_with()
            mock_timeout.assert_called_once_with(total=30)
            mock_session.assert_called_once()
            assert session == mock_session_instance

    @pytest.mark.asyncio
    async def test_create_session_with_custom_timeout(self):
        """Test creating a session with custom timeout."""
        with (
            patch("src.grpy_request_client.managers.session_manager.ClientSession") as mock_session,
            patch(
                "src.grpy_request_client.managers.session_manager.TCPConnector"
            ) as mock_connector,
            patch("src.grpy_request_client.managers.session_manager.ClientTimeout") as mock_timeout,
        ):
            # Setup mocks
            mock_session_instance = MagicMock(spec=ClientSession)
            mock_session.return_value = mock_session_instance

            # Call the method with custom timeout
            session = SessionManager.create_session(timeout=60)

            # Verify timeout was created with expected value
            mock_connector.assert_called_once_with()
            mock_timeout.assert_called_once_with(total=60)
            mock_session.assert_called_once()
            assert session == mock_session_instance

    @pytest.mark.asyncio
    async def test_create_session_with_connector_options(self):
        """Test creating a session with custom connector options."""
        with (
            patch("src.grpy_request_client.managers.session_manager.ClientSession") as mock_session,
            patch(
                "src.grpy_request_client.managers.session_manager.TCPConnector"
            ) as mock_connector,
            patch("src.grpy_request_client.managers.session_manager.ClientTimeout") as mock_timeout,
        ):
            # Setup mocks
            mock_session_instance = MagicMock(spec=ClientSession)
            mock_session.return_value = mock_session_instance

            # Call the method with connector options
            connector_options = {"limit": 20, "ssl": False}
            session = SessionManager.create_session(connector_options=connector_options)

            # Verify connector was created with expected options
            mock_connector.assert_called_once_with(**connector_options)
            mock_timeout.assert_called_once_with(total=30)
            mock_session.assert_called_once()
            assert session == mock_session_instance

    @pytest.mark.asyncio
    async def test_get_shared_session_creates_new_if_none_exists(self):
        """Test that get_shared_session creates a new session if none exists."""
        # Reset the singleton state
        SessionManager._shared_session = None

        with patch.object(SessionManager, "create_session") as mock_create:
            mock_session = MagicMock(spec=ClientSession)
            mock_session.closed = False
            mock_create.return_value = mock_session

            # Call get_shared_session
            session = SessionManager.get_shared_session()

            # Verify create_session was called and returned session is correct
            mock_create.assert_called_once()
            assert session == mock_session
            assert SessionManager._shared_session == mock_session

    @pytest.mark.asyncio
    async def test_get_shared_session_returns_existing_session(self):
        """Test that get_shared_session returns existing session if available."""
        # Setup existing session
        mock_session = MagicMock(spec=ClientSession)
        mock_session.closed = False
        SessionManager._shared_session = mock_session

        with patch.object(SessionManager, "create_session") as mock_create:
            # Call get_shared_session
            session = SessionManager.get_shared_session()

            # Verify create_session was not called and existing session is returned
            mock_create.assert_not_called()
            assert session == mock_session

    @pytest.mark.asyncio
    async def test_get_shared_session_creates_new_if_existing_closed(self):
        """Test that get_shared_session creates a new session if existing one is closed."""
        # Setup closed session
        mock_closed_session = MagicMock(spec=ClientSession)
        mock_closed_session.closed = True
        SessionManager._shared_session = mock_closed_session

        with patch.object(SessionManager, "create_session") as mock_create:
            mock_new_session = MagicMock(spec=ClientSession)
            mock_new_session.closed = False
            mock_create.return_value = mock_new_session

            # Call get_shared_session
            session = SessionManager.get_shared_session()

            # Verify create_session was called and new session is returned
            mock_create.assert_called_once()
            assert session == mock_new_session
            assert SessionManager._shared_session == mock_new_session

    @pytest.mark.asyncio
    async def test_get_shared_session_with_custom_params(self):
        """Test that get_shared_session passes parameters to create_session."""
        # Reset the singleton state
        SessionManager._shared_session = None

        with patch.object(SessionManager, "create_session") as mock_create:
            mock_session = MagicMock(spec=ClientSession)
            mock_session.closed = False
            mock_create.return_value = mock_session

            # Call get_shared_session with custom parameters
            session = SessionManager.get_shared_session(timeout=60, custom_param="test")

            # Verify create_session was called with the parameters
            # Note: The first parameter (timeout) is passed positionally in the actual implementation
            mock_create.assert_called_once_with(60, custom_param="test")
            assert session == mock_session

    @pytest.mark.asyncio
    async def test_close_shared_session(self):
        """Test closing the shared session."""
        # Setup mock session with AsyncMock for close method
        mock_session = MagicMock(spec=ClientSession)
        mock_session.closed = False
        mock_session.close = AsyncMock()
        SessionManager._shared_session = mock_session

        # Call close_shared_session
        await SessionManager.close_shared_session()

        # Verify session was closed
        mock_session.close.assert_called_once()
        assert SessionManager._shared_session is None

    @pytest.mark.asyncio
    async def test_close_shared_session_with_no_session(self):
        """Test closing when no session exists."""
        # Ensure no session exists
        SessionManager._shared_session = None

        # This should not raise any errors
        await SessionManager.close_shared_session()

    @pytest.mark.asyncio
    async def test_close_shared_session_with_already_closed_session(self):
        """Test closing when session is already closed."""
        # Setup already closed session
        mock_session = MagicMock(spec=ClientSession)
        mock_session.closed = True
        mock_session.close = AsyncMock()
        SessionManager._shared_session = mock_session

        # Call close_shared_session
        await SessionManager.close_shared_session()

        # Verify close was not called on already closed session
        mock_session.close.assert_not_called()
        # Session should remain as-is since it's already closed
        # (the implementation only clears sessions that are successfully closed)
        assert SessionManager._shared_session == mock_session

    @pytest.mark.asyncio
    async def test_create_session_always_returns_new_instance(self):
        """Test that create_session always returns a new session instance."""
        with patch.object(
            SessionManager, "create_session", wraps=SessionManager.create_session
        ) as mock_create:
            with (
                patch(
                    "src.grpy_request_client.managers.session_manager.ClientSession"
                ) as mock_session_class,
                patch("src.grpy_request_client.managers.session_manager.TCPConnector"),
                patch("src.grpy_request_client.managers.session_manager.ClientTimeout"),
            ):
                # Setup mocks to return different instances
                mock_session1 = MagicMock(spec=ClientSession)
                mock_session2 = MagicMock(spec=ClientSession)
                mock_session_class.side_effect = [mock_session1, mock_session2]

                # Call create_session twice
                session1 = SessionManager.create_session()
                session2 = SessionManager.create_session()

                # Verify both calls returned different instances
                assert session1 == mock_session1
                assert session2 == mock_session2
                assert session1 != session2
                assert mock_create.call_count == 2

    @pytest.mark.asyncio
    async def test_shared_session_lifecycle(self):
        """Test the complete lifecycle of a shared session."""
        # Reset state
        SessionManager._shared_session = None

        with patch.object(SessionManager, "create_session") as mock_create:
            mock_session = MagicMock(spec=ClientSession)
            mock_session.closed = False
            mock_session.close = AsyncMock()
            mock_create.return_value = mock_session

            # Get shared session (should create new)
            session1 = SessionManager.get_shared_session()
            assert session1 == mock_session
            assert SessionManager._shared_session == mock_session
            mock_create.assert_called_once()

            # Get shared session again (should return existing)
            session2 = SessionManager.get_shared_session()
            assert session2 == mock_session
            assert session1 is session2
            # create_session should still only be called once
            mock_create.assert_called_once()

            # Close shared session
            await SessionManager.close_shared_session()
            mock_session.close.assert_called_once()
            assert SessionManager._shared_session is None

            # Get shared session after closing (should create new)
            mock_create.reset_mock()
            mock_new_session = MagicMock(spec=ClientSession)
            mock_new_session.closed = False
            mock_create.return_value = mock_new_session

            session3 = SessionManager.get_shared_session()
            assert session3 == mock_new_session
            assert session3 != mock_session
            mock_create.assert_called_once()

    def test_create_session_with_session_options(self):
        """Test creating a session with custom session options."""
        with (
            patch("src.grpy_request_client.managers.session_manager.ClientSession") as mock_session,
            patch(
                "src.grpy_request_client.managers.session_manager.TCPConnector"
            ) as mock_connector,
            patch("src.grpy_request_client.managers.session_manager.ClientTimeout") as mock_timeout,
        ):
            # Setup mocks
            mock_session_instance = MagicMock(spec=ClientSession)
            mock_session.return_value = mock_session_instance

            # Call the method with session options
            session_options = {"headers": {"User-Agent": "test"}, "trust_env": True}
            session = SessionManager.create_session(session_options=session_options)

            # Verify session was created with expected options
            mock_connector.assert_called_once_with()
            mock_timeout.assert_called_once_with(total=30)
            mock_session.assert_called_once_with(
                connector=mock_connector.return_value,
                timeout=mock_timeout.return_value,
                **session_options,
            )
            assert session == mock_session_instance

    def test_create_session_with_both_connector_and_session_options(self):
        """Test creating a session with both connector and session options."""
        with (
            patch("src.grpy_request_client.managers.session_manager.ClientSession") as mock_session,
            patch(
                "src.grpy_request_client.managers.session_manager.TCPConnector"
            ) as mock_connector,
            patch("src.grpy_request_client.managers.session_manager.ClientTimeout") as mock_timeout,
        ):
            # Setup mocks
            mock_session_instance = MagicMock(spec=ClientSession)
            mock_session.return_value = mock_session_instance

            # Call the method with both types of options
            connector_options = {"limit": 20, "ssl": False}
            session_options = {"headers": {"User-Agent": "test"}}
            session = SessionManager.create_session(
                connector_options=connector_options, session_options=session_options
            )

            # Verify both types of options were used
            mock_connector.assert_called_once_with(**connector_options)
            mock_timeout.assert_called_once_with(total=30)
            mock_session.assert_called_once_with(
                connector=mock_connector.return_value,
                timeout=mock_timeout.return_value,
                **session_options,
            )
            assert session == mock_session_instance
