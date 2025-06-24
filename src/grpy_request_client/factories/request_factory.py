from ..models.request_model import RequestModel
from ..managers.session_manager import SessionManager


class RequestFactory:
    """Factory class for creating RequestModel instances."""

    @staticmethod
    def create_request(data: dict) -> RequestModel:
        """
        Create a RequestModel instance from serialized data.

        Args:
            data: Dictionary containing request configuration data

        Returns:
            RequestModel: Configured RequestModel instance
        """
        return RequestModel(**data)

    @staticmethod
    def create_session(**kwargs):
        """
        Create a session object using SessionManager.

        Args:
            **kwargs: Additional options for session creation

        Returns:
            ClientSession: Configured session instance
        """
        return SessionManager.get_session(**kwargs)
