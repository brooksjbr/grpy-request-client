from aiohttp import ClientSession, ClientTimeout, TCPConnector


class SessionManager:
    """Manager class for creating and managing ClientSession instances."""

    # Singleton instance
    _instance = None
    _session = None

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_session(cls, timeout: int = 30, **kwargs) -> ClientSession:
        """
        Get or create a shared ClientSession instance.

        Args:
            timeout: Request timeout in seconds
            **kwargs: Additional options for connector and session

        Returns:
            A shared ClientSession instance
        """
        if cls._session is None or cls._session.closed:
            cls._session = cls.create_session(timeout, **kwargs)
        return cls._session

    @classmethod
    def create_session(cls, timeout: int = 30, **kwargs) -> ClientSession:
        """
        Create a new ClientSession with the specified configuration.

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
    async def close_session(cls):
        """Close the shared session if it exists."""
        if cls._session and not cls._session.closed:
            await cls._session.close()
            cls._session = None
