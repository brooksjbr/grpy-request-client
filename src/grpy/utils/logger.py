import logging
import sys
from typing import Any, Optional, Protocol, runtime_checkable


@runtime_checkable
class LoggerProtocol(Protocol):
    """Protocol defining the logger interface."""

    def debug(self, message: str, **kwargs: Any) -> None:
        ...

    def info(self, message: str, **kwargs: Any) -> None:
        ...

    def warning(self, message: str, **kwargs: Any) -> None:
        ...

    def error(self, message: str, **kwargs: Any) -> None:
        ...

    def critical(self, message: str, **kwargs: Any) -> None:
        ...


class ComponentLogger:
    """Wrapper that adds component identification to log messages."""

    def __init__(self, logger: LoggerProtocol, component_name: str):
        """Initialize the component logger.

        Args:
            logger: The base logger instance to wrap
            component_name: Name of the component for identification
        """
        self._logger = logger
        self._component_name = component_name

    def _add_component_context(self, message: str, **kwargs):
        """Add component name to message and kwargs.

        Args:
            message: The log message
            **kwargs: Additional context

        Returns:
            Tuple of (prefixed_message, updated_kwargs)
        """
        prefixed_message = f"[{self._component_name}] {message}"
        kwargs["component"] = self._component_name
        return prefixed_message, kwargs

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message with component identification."""
        msg, kw = self._add_component_context(message, **kwargs)
        self._logger.debug(msg, **kw)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message with component identification."""
        msg, kw = self._add_component_context(message, **kwargs)
        self._logger.info(msg, **kw)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message with component identification."""
        msg, kw = self._add_component_context(message, **kwargs)
        self._logger.warning(msg, **kw)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message with component identification."""
        msg, kw = self._add_component_context(message, **kwargs)
        self._logger.error(msg, **kw)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log a critical message with component identification."""
        msg, kw = self._add_component_context(message, **kwargs)
        self._logger.critical(msg, **kw)


class Logger:
    """Base logger class for grpy-request-client.

    Provides standardized logging functionality with configurable levels
    and formatting for the REST client operations.
    """

    # Log levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __init__(
        self,
        name: str = "grpy-request-client",
        level: int = logging.INFO,
        format_string: Optional[str] = None,
        log_to_console: bool = True,
        log_file: Optional[str] = None,
    ):
        """Initialize the logger.

        Args:
            name: Logger name
            level: Minimum logging level
            format_string: Custom format string for log messages
            log_to_console: Whether to log to console
            log_file: Optional file path to log to
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Clear any existing handlers
        if self.logger.handlers:
            self.logger.handlers.clear()

        # Default format
        if format_string is None:
            format_string = "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"

        formatter = logging.Formatter(format_string)

        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def get_component_logger(self, component_name: str) -> ComponentLogger:
        """Get a component-aware logger for a specific component.

        Args:
            component_name: Name of the component for identification

        Returns:
            ComponentLogger instance that prefixes all messages with component name
        """
        return ComponentLogger(self, component_name)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message.

        Args:
            message: The message to log
            **kwargs: Additional context to include in the log
        """
        self._log(self.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message.

        Args:
            message: The message to log
            **kwargs: Additional context to include in the log
        """
        self._log(self.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message.

        Args:
            message: The message to log
            **kwargs: Additional context to include in the log
        """
        self._log(self.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message.

        Args:
            message: The message to log
            **kwargs: Additional context to include in the log
        """
        self._log(self.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log a critical message.

        Args:
            message: The message to log
            **kwargs: Additional context to include in the log
        """
        self._log(self.CRITICAL, message, **kwargs)

    def _log(self, level: int, message: str, **kwargs: Any) -> None:
        """Internal method to handle logging with context.

        Args:
            level: Log level
            message: The message to log
            **kwargs: Additional context to include in the log
        """
        if kwargs:
            context_str = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            message = f"{message} - {context_str}"
        self.logger.log(level, message)
