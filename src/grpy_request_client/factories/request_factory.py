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
    def create_shared_session(**kwargs):
        """
        Create/get a shared session object using SessionManager singleton.

        This returns the same session instance across calls (singleton pattern).
        The session lifecycle should be managed at the application level.

        Args:
            **kwargs: Additional options for session creation

        Returns:
            ClientSession: Shared session instance
        """
        return SessionManager.get_shared_session(**kwargs)

    @staticmethod
    def create_session(**kwargs):
        """
        Create a new independent session object.

        This creates a completely new session that is not shared.
        The caller is responsible for managing its lifecycle.

        Args:
            **kwargs: Additional options for session creation

        Returns:
            ClientSession: New independent session instance
        """
        return SessionManager.create_session(**kwargs)

    @staticmethod
    def get_shared_session(**kwargs):
        """
        Alias for create_shared_session for backward compatibility.

        Args:
            **kwargs: Additional options for session creation

        Returns:
            ClientSession: Shared session instance
        """
        return SessionManager.get_shared_session(**kwargs)

    @staticmethod
    def create_request_manager(
        request_data: RequestModel, session=None, logger=None, use_shared_session=False
    ) -> RequestManager:
        """
        Create a RequestManager instance.

        Args:
            request_data: RequestModel containing request configuration
            session: Optional ClientSession to use for requests. If not provided,
                    RequestManager will create its own session when used as a context manager.
            logger: Optional logger instance
            use_shared_session: If True and no session provided, use the shared singleton session

        Returns:
            RequestManager: Configured RequestManager instance
        """
        if session is None and use_shared_session:
            session = SessionManager.get_shared_session()

        return RequestManager(request_data, session, logger)

    @staticmethod
    def create_request_manager_with_shared_session(
        request_data: RequestModel, logger=None, **session_kwargs
    ) -> RequestManager:
        """
        Create a RequestManager instance with the shared session.

        This is a convenience method for when you want to use the shared session.

        Args:
            request_data: RequestModel containing request configuration
            logger: Optional logger instance
            **session_kwargs: Additional options for shared session creation

        Returns:
            RequestManager: Configured RequestManager instance with shared session
        """
        session = SessionManager.get_shared_session(**session_kwargs)
        return RequestManager(request_data, session, logger)

    @staticmethod
    def create_request_manager_with_new_session(
        request_data: RequestModel, logger=None, **session_kwargs
    ) -> RequestManager:
        """
        Create a RequestManager instance with a new independent session.

        The RequestManager will take ownership of this session and close it
        when used as a context manager.

        Args:
            request_data: RequestModel containing request configuration
            logger: Optional logger instance
            **session_kwargs: Additional options for session creation

        Returns:
            RequestManager: Configured RequestManager instance with new session
        """
        session = SessionManager.create_session(**session_kwargs)
        return RequestManager(request_data, session, logger)
