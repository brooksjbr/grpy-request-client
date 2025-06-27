from aiohttp import ClientSession, ClientTimeout, TCPConnector


class SessionManager:
    """Manager class for creating and managing ClientSession instances."""

    # Singleton instance
    _instance = None
    _shared_session = None

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_shared_session(cls, timeout: int = 30, **kwargs) -> ClientSession:
        """
        Get or create a shared ClientSession instance (singleton pattern).

        This method maintains the original behavior for backward compatibility.
        The shared session should be managed at the application level.

        Args:
            timeout: Request timeout in seconds
            **kwargs: Additional options for connector and session

        Returns:
            A shared ClientSession instance
        """
        if cls._shared_session is None or cls._shared_session.closed:
            cls._shared_session = cls.create_session(timeout, **kwargs)
        return cls._shared_session

    @classmethod
    def get_session(cls, timeout: int = 30, **kwargs) -> ClientSession:
        """
        Alias for get_shared_session for backward compatibility.

        Args:
            timeout: Request timeout in seconds
            **kwargs: Additional options for connector and session

        Returns:
            A shared ClientSession instance
        """
        return cls.get_shared_session(timeout, **kwargs)

    @classmethod
    def create_session(cls, timeout: int = 30, **kwargs) -> ClientSession:
        """
        Create a new ClientSession with the specified configuration.

        This creates a completely new session instance that is not managed
        by the SessionManager singleton. The caller is responsible for
        closing this session.

        Args:
            timeout: Request timeout in seconds
            **kwargs: Additional options for connector and session

        Returns:
            A new ClientSession instance
        """
        connector = TCPConnector(**kwargs.get("connector_options", {}))
        timeout_obj = ClientTimeout(total=timeout)
        return ClientSession(
            connector=connector, timeout=timeout_obj, **kwargs.get("session_options", {})
        )

    @classmethod
    async def close_shared_session(cls):
        """Close the shared session if it exists."""
        if cls._shared_session and not cls._shared_session.closed:
            await cls._shared_session.close()
            cls._shared_session = None

    @classmethod
    async def close_session(cls):
        """Alias for close_shared_session for backward compatibility."""
        await cls.close_shared_session()
