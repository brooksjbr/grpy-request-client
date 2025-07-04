from asyncio import TimeoutError
from contextlib import AsyncExitStack
from typing import AsyncContextManager, Optional
from urllib.parse import urljoin

from aiohttp import (
    ClientConnectionError,
    ClientConnectorSSLError,
    ClientResponseError,
    ClientSession,
)

from ..models.request_model import RequestModel
from ..utils.logger import ComponentLogger, Logger, LoggerProtocol


class RequestManager(AsyncContextManager["RequestManager"]):
    """
    HTTP Request class that handles request data and acts as an async context manager.

    This class encapsulates the logic for executing HTTP requests based on the
    configuration in a RestClientModel. It handles error responses by raising
    appropriate exceptions for different status codes.

    Key features:
    - Works as an async context manager
    - Executes HTTP requests using aiohttp
    - Automatically raises exceptions for non-2xx responses
    - Supports all standard HTTP methods (GET, POST, PUT, DELETE, PATCH, HEAD)
    - Can work with or without an external session (creates its own if needed)

    """

    requestData: RequestModel
    session: Optional[ClientSession]
    logger: LoggerProtocol
    _exit_stack: Optional[AsyncExitStack] = None
    _owns_session: bool = False

    def __init__(
        self,
        requestData: RequestModel,
        session: Optional[ClientSession] = None,
        logger: Optional[LoggerProtocol] = None,
    ) -> None:
        """
        Initialize the HTTP request with request data and an optional session.

        Args:
            requestData: The RequestModel containing request configuration
            session: Optional ClientSession to use for requests. If not provided,
                    a new session will be created when needed.
            logger: Optional logger instance. If not provided, a default Logger will be created
        """
        self.requestData = requestData
        self.session = session
        self._owns_session = session is None

        # Create component-aware logger
        if logger is None:
            base_logger = Logger()
            self.logger = base_logger.get_component_logger("RequestManager")
        elif isinstance(logger, Logger):
            self.logger = logger.get_component_logger("RequestManager")
        else:
            # Fallback for loggers that don't support get_component_logger
            self.logger = ComponentLogger(logger, "RequestManager")

    async def __aenter__(self):
        """
        Enter the async context manager.

        Sets up the exit stack for resource management and creates a session if needed.

        Returns:
            The RequestManager instance
        """
        self._exit_stack = AsyncExitStack()

        # Create session if we don't have one
        if self.session is None:
            self.session = ClientSession()
            self._owns_session = True
            # Register the session for cleanup
            await self._exit_stack.enter_async_context(self.session)
            self.logger.debug("Created new session for RequestManager")
        else:
            # Mark external session so we don't close it
            self.session._external = True
            self.logger.debug("Using external session for RequestManager")

        self.logger.debug("Entering RequestManager context manager")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the async context manager.

        Cleans up the exit stack and closes the session if we own it.
        """
        try:
            if self._exit_stack:
                await self._exit_stack.aclose()
        finally:
            # Reset session reference if we owned it
            if self._owns_session:
                self.session = None
            self._exit_stack = None
            self.logger.debug("Exiting RequestManager context manager")

    async def _ensure_session(self) -> ClientSession:
        """
        Ensure we have a session available for making requests.

        Returns:
            ClientSession: The session to use for requests

        Raises:
            RuntimeError: If called outside of context manager when no session is provided
        """
        if self.session is None:
            raise RuntimeError(
                "No session available. Either provide a session during initialization "
                "or use RequestManager as an async context manager."
            )
        return self.session

    async def execute_request(self):
        """
        Execute the HTTP request using the configured session and request data.

        This method performs the HTTP request according to the configuration in the
        requestData object. It automatically handles error responses by raising
        appropriate exceptions.

        Returns:
            ClientResponse: The response from the HTTP request for successful (2xx) responses

        Raises:
            RuntimeError: If no session is available (not used as context manager and no session provided)
            ClientResponseError: For HTTP error responses, including:
                             - 401 Unauthorized (authentication failures)
                             - 403 Forbidden (authorization failures)
                             - Other 4xx client errors
                             - 5xx server errors
            ClientConnectorSSLError: For SSL certificate validation failures
            ClientConnectionError: For network connection issues
            asyncio.TimeoutError: When the request times out
            Exception: Any other exceptions that occur during the request
        """
        # Ensure we have a session
        session = await self._ensure_session()

        url = urljoin(str(self.requestData.base_url), self.requestData.endpoint)

        # Prepare request kwargs
        kwargs = {
            "params": self.requestData.params,
            "headers": self.requestData.headers,
            "timeout": self.requestData.timeout,
        }

        # Add data if present
        if self.requestData.data is not None:
            kwargs["json"] = self.requestData.data

        self.logger.info(
            f"Executing {self.requestData.method} request",
            url=url,
            endpoint=self.requestData.endpoint,
        )

        try:
            # Execute the request
            response = await session.request(method=self.requestData.method, url=url, **kwargs)

            self.logger.info(
                "Received response", status=response.status, reason=response.reason, url=url
            )

            # Check for error status codes
            if response.status == 401:
                # Authentication error (Unauthorized)
                error_message = f"Authentication failed: {response.status} {response.reason}"
                self.logger.error(error_message, status=response.status, url=url)
                raise ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=error_message,
                    headers=response.headers,
                )
            elif response.status == 403:
                # Authorization error (Forbidden)
                error_message = f"Authorization failed: {response.status} {response.reason}"
                self.logger.error(error_message, status=response.status, url=url)
                raise ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=error_message,
                    headers=response.headers,
                )
            elif 400 <= response.status < 500:
                # Other client errors (4xx)
                error_message = f"{response.status} {response.reason}"
                self.logger.warning(
                    f"Client error: {error_message}", status=response.status, url=url
                )
                raise ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=error_message,
                    headers=response.headers,
                )
            elif 500 <= response.status < 600:
                # Server error (5xx)
                error_message = f"{response.status} {response.reason}"
                self.logger.error(f"Server error: {error_message}", status=response.status, url=url)
                raise ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=error_message,
                    headers=response.headers,
                )
            self.logger.info("Request completed successfully", status=response.status, url=url)
            return response

        except ClientConnectorSSLError as e:
            # SSL certificate validation errors
            self.logger.error(f"SSL certificate validation error: {str(e)}", url=url)
            raise e
        except ClientConnectionError as e:
            # Network connection issues (DNS failures, connection refused, etc.)
            self.logger.error(f"Connection error: {str(e)}", url=url)
            raise e
        except TimeoutError as e:
            # Request timeout
            self.logger.error(f"Request timeout: {str(e)}", url=url)
            raise e
        except Exception as e:
            # Catch-all for any other exceptions
            self.logger.critical(f"Unexpected error during request: {str(e)}", url=url)
            raise e
