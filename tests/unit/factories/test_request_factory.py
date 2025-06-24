import pytest
from unittest.mock import patch

from src.grpy_request_client.factories.request_factory import RequestFactory
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
        assert request.endpoint == ""   # default value

    def test_create_request_with_invalid_data(self, invalid_request_data):
        """Test creating a RequestModel with invalid data raises error."""
        with pytest.raises(Exception):  # Pydantic validation error
            RequestFactory.create_request(invalid_request_data)

    def test_create_request_with_missing_required_data(self):
        """Test creating a RequestModel with missing required data raises error."""
        data = {}

        with pytest.raises(Exception):  # Pydantic validation error
            RequestFactory.create_request(data)

    @patch('src.grpy_request_client.factories.request_factory.SessionManager')
    def test_create_session_calls_session_manager(self, mock_session_manager, mock_session):
        """Test that create_session calls SessionManager.get_session."""
        mock_session_manager.get_session.return_value = mock_session

        session = RequestFactory.create_session()

        mock_session_manager.get_session.assert_called_once_with()
        assert session == mock_session

    @patch('src.grpy_request_client.factories.request_factory.SessionManager')
    def test_create_session_with_kwargs(self, mock_session_manager, mock_session):
        """Test that create_session passes kwargs to SessionManager."""
        mock_session_manager.get_session.return_value = mock_session

        session = RequestFactory.create_session(timeout=60, custom_param="test")

        mock_session_manager.get_session.assert_called_once_with(timeout=60, custom_param="test")
        assert session == mock_session

    @patch('src.grpy_request_client.factories.request_factory.SessionManager')
    def test_create_session_returns_session_object(self, mock_session_manager, mock_session):
        """Test that create_session returns a session object."""
        mock_session_manager.get_session.return_value = mock_session

        session = RequestFactory.create_session()

        assert session is not None
        assert session == mock_session
