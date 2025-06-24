from ..managers.request_manager import RequestManager
from ..managers.session_manager import SessionManager
from ..models.request_model import RequestModel


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

    @staticmethod
    def create_request_manager(request_data: RequestModel, session, logger=None) -> RequestManager:
        """
        Create a RequestManager instance.

        Args:
            request_data: RequestModel containing request configuration
            session: ClientSession to use for requests
            logger: Optional logger instance

        Returns:
            RequestManager: Configured RequestManager instance
        """
        return RequestManager(request_data, session, logger)
