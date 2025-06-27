from unittest.mock import MagicMock, patch

import pytest

from src.grpy_request_client.factories.request_factory import RequestFactory
from src.grpy_request_client.managers.request_manager import RequestManager
from src.grpy_request_client.models.request_model import RequestModel


class TestRequestFactory:
    """Test suite for RequestFactory."""

    def test_create_request_with_valid_data(self, valid_request_data, base_url):
        """Test creating a RequestModel with valid data."""
        request = RequestFactory.create_request(valid_request_data)

        assert isinstance(request, RequestModel)
        assert str(request.base_url) == base_url
        assert request.method == "GET"
        assert request.endpoint == "/users"
        assert request.timeout == 30.0

    def test_create_request_with_minimal_data(self, minimal_request_data, base_url):
        """Test creating a RequestModel with minimal required data."""
        request = RequestFactory.create_request(minimal_request_data)

        assert isinstance(request, RequestModel)
        assert str(request.base_url) == base_url
        assert request.method == "GET"  # default value
        assert request.endpoint == ""  # default value

    def test_create_request_with_invalid_data(self, invalid_request_data):
        """Test creating a RequestModel with invalid data raises error."""
        with pytest.raises(Exception):  # Pydantic validation error
            RequestFactory.create_request(invalid_request_data)

    def test_create_request_with_missing_required_data(self):
        """Test creating a RequestModel with missing required data raises error."""
        data = {}

        with pytest.raises(Exception):  # Pydantic validation error
            RequestFactory.create_request(data)

    @patch("src.grpy_request_client.factories.request_factory.SessionManager")
    def test_create_session_calls_session_manager_create_session(
        self, mock_session_manager, mock_session
    ):
        """Test that create_session calls SessionManager.create_session."""
        mock_session_manager.create_session.return_value = mock_session

        session = RequestFactory.create_session()

        mock_session_manager.create_session.assert_called_once_with()
        assert session == mock_session

    @patch("src.grpy_request_client.factories.request_factory.SessionManager")
    def test_create_session_with_kwargs(self, mock_session_manager, mock_session):
        """Test that create_session passes kwargs to SessionManager.create_session."""
        mock_session_manager.create_session.return_value = mock_session

        session = RequestFactory.create_session(timeout=60, custom_param="test")

        mock_session_manager.create_session.assert_called_once_with(timeout=60, custom_param="test")
        assert session == mock_session

    @patch("src.grpy_request_client.factories.request_factory.SessionManager")
    def test_create_session_returns_session_object(self, mock_session_manager, mock_session):
        """Test that create_session returns a session object."""
        mock_session_manager.create_session.return_value = mock_session

        session = RequestFactory.create_session()

        assert session is not None
        assert session == mock_session

    @patch("src.grpy_request_client.factories.request_factory.SessionManager")
    def test_create_shared_session_calls_session_manager_get_shared_session(
        self, mock_session_manager, mock_session
    ):
        """Test that create_shared_session calls SessionManager.get_shared_session."""
        mock_session_manager.get_shared_session.return_value = mock_session

        session = RequestFactory.create_shared_session()

        mock_session_manager.get_shared_session.assert_called_once_with()
        assert session == mock_session

    @patch("src.grpy_request_client.factories.request_factory.SessionManager")
    def test_create_shared_session_with_kwargs(self, mock_session_manager, mock_session):
        """Test that create_shared_session passes kwargs to SessionManager."""
        mock_session_manager.get_shared_session.return_value = mock_session

        session = RequestFactory.create_shared_session(timeout=60, custom_param="test")

        mock_session_manager.get_shared_session.assert_called_once_with(
            timeout=60, custom_param="test"
        )
        assert session == mock_session

    @patch("src.grpy_request_client.factories.request_factory.SessionManager")
    def test_get_shared_session_calls_session_manager(self, mock_session_manager, mock_session):
        """Test that get_shared_session calls SessionManager.get_shared_session."""
        mock_session_manager.get_shared_session.return_value = mock_session

        session = RequestFactory.get_shared_session()

        mock_session_manager.get_shared_session.assert_called_once_with()
        assert session == mock_session

    @patch("src.grpy_request_client.factories.request_factory.RequestManager")
    def test_create_request_manager_with_required_params(
        self, mock_request_manager, valid_request_data, mock_session
    ):
        """Test creating a RequestManager with required parameters."""
        request_data = RequestFactory.create_request(valid_request_data)
        mock_manager_instance = MagicMock(spec=RequestManager)
        mock_request_manager.return_value = mock_manager_instance

        manager = RequestFactory.create_request_manager(request_data, mock_session)

        mock_request_manager.assert_called_once_with(request_data, mock_session, None)
        assert manager == mock_manager_instance

    @patch("src.grpy_request_client.factories.request_factory.RequestManager")
    def test_create_request_manager_without_session(self, mock_request_manager, valid_request_data):
        """Test creating a RequestManager without session parameter."""
        request_data = RequestFactory.create_request(valid_request_data)
        mock_manager_instance = MagicMock(spec=RequestManager)
        mock_request_manager.return_value = mock_manager_instance

        manager = RequestFactory.create_request_manager(request_data)

        mock_request_manager.assert_called_once_with(request_data, None, None)
        assert manager == mock_manager_instance

    @patch("src.grpy_request_client.factories.request_factory.RequestManager")
    def test_create_request_manager_with_use_shared_session_true(
        self, mock_request_manager, valid_request_data
    ):
        """Test creating a RequestManager with use_shared_session=True."""
        request_data = RequestFactory.create_request(valid_request_data)
        mock_manager_instance = MagicMock(spec=RequestManager)
        mock_request_manager.return_value = mock_manager_instance

        with patch(
            "src.grpy_request_client.factories.request_factory.SessionManager"
        ) as mock_session_manager:
            mock_shared_session = MagicMock()
            mock_session_manager.get_shared_session.return_value = mock_shared_session

            manager = RequestFactory.create_request_manager(request_data, use_shared_session=True)

            mock_session_manager.get_shared_session.assert_called_once()
            mock_request_manager.assert_called_once_with(request_data, mock_shared_session, None)
            assert manager == mock_manager_instance

    @patch("src.grpy_request_client.factories.request_factory.RequestManager")
    def test_create_request_manager_with_logger(
        self, mock_request_manager, valid_request_data, mock_session
    ):
        """Test creating a RequestManager with logger parameter."""
        request_data = RequestFactory.create_request(valid_request_data)
        mock_logger = MagicMock()
        mock_manager_instance = MagicMock(spec=RequestManager)
        mock_request_manager.return_value = mock_manager_instance

        manager = RequestFactory.create_request_manager(request_data, mock_session, mock_logger)

        mock_request_manager.assert_called_once_with(request_data, mock_session, mock_logger)
        assert manager == mock_manager_instance

    @patch("src.grpy_request_client.factories.request_factory.RequestManager")
    def test_create_request_manager_returns_manager_instance(
        self, mock_request_manager, valid_request_data, mock_session
    ):
        """Test that create_request_manager returns a RequestManager instance."""
        request_data = RequestFactory.create_request(valid_request_data)
        mock_manager_instance = MagicMock(spec=RequestManager)
        mock_request_manager.return_value = mock_manager_instance

        manager = RequestFactory.create_request_manager(request_data, mock_session)

        assert manager is not None
        assert manager == mock_manager_instance
        assert isinstance(manager, type(mock_manager_instance))

    def test_create_request_manager_integration(self, valid_request_data, mock_session):
        """Test creating a RequestManager without mocking (integration test)."""
        request_data = RequestFactory.create_request(valid_request_data)

        manager = RequestFactory.create_request_manager(request_data, mock_session)

        assert isinstance(manager, RequestManager)
        assert manager.requestData == request_data
        assert manager.session == mock_session
        assert manager._owns_session is False

    def test_create_request_manager_integration_without_session(self, valid_request_data):
        """Test creating a RequestManager without session (integration test)."""
        request_data = RequestFactory.create_request(valid_request_data)

        manager = RequestFactory.create_request_manager(request_data)

        assert isinstance(manager, RequestManager)
        assert manager.requestData == request_data
        assert manager.session is None
        assert manager._owns_session is True

    @patch("src.grpy_request_client.factories.request_factory.SessionManager")
    @patch("src.grpy_request_client.factories.request_factory.RequestManager")
    def test_create_request_manager_with_shared_session_method(
        self, mock_request_manager, mock_session_manager, valid_request_data
    ):
        """Test create_request_manager_with_shared_session method."""
        request_data = RequestFactory.create_request(valid_request_data)
        mock_shared_session = MagicMock()
        mock_session_manager.get_shared_session.return_value = mock_shared_session
        mock_manager_instance = MagicMock(spec=RequestManager)
        mock_request_manager.return_value = mock_manager_instance

        manager = RequestFactory.create_request_manager_with_shared_session(
            request_data, timeout=60, custom_param="test"
        )

        mock_session_manager.get_shared_session.assert_called_once_with(
            timeout=60, custom_param="test"
        )
        mock_request_manager.assert_called_once_with(request_data, mock_shared_session, None)
        assert manager == mock_manager_instance

    @patch("src.grpy_request_client.factories.request_factory.SessionManager")
    @patch("src.grpy_request_client.factories.request_factory.RequestManager")
    def test_create_request_manager_with_new_session_method(
        self, mock_request_manager, mock_session_manager, valid_request_data
    ):
        """Test create_request_manager_with_new_session method."""
        request_data = RequestFactory.create_request(valid_request_data)
        mock_new_session = MagicMock()
        mock_session_manager.create_session.return_value = mock_new_session
        mock_manager_instance = MagicMock(spec=RequestManager)
        mock_request_manager.return_value = mock_manager_instance

        manager = RequestFactory.create_request_manager_with_new_session(
            request_data, timeout=60, custom_param="test"
        )

        mock_session_manager.create_session.assert_called_once_with(timeout=60, custom_param="test")
        mock_request_manager.assert_called_once_with(request_data, mock_new_session, None)
        assert manager == mock_manager_instance

    def test_session_creation_methods_return_different_types(self):
        """Test that different session creation methods work as expected."""
        with patch(
            "src.grpy_request_client.factories.request_factory.SessionManager"
        ) as mock_session_manager:
            mock_new_session = MagicMock()
            mock_shared_session = MagicMock()
            mock_session_manager.create_session.return_value = mock_new_session
            mock_session_manager.get_shared_session.return_value = mock_shared_session

            new_session = RequestFactory.create_session()
            shared_session1 = RequestFactory.create_shared_session()
            shared_session2 = RequestFactory.get_shared_session()

            assert new_session == mock_new_session
            assert shared_session1 == mock_shared_session
            assert shared_session2 == mock_shared_session

            # Verify the correct methods were called
            mock_session_manager.create_session.assert_called_once()
            assert mock_session_manager.get_shared_session.call_count == 2
