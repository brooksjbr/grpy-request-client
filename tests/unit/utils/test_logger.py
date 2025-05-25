import logging
import sys
from io import StringIO
from unittest.mock import Mock, patch

import pytest

from grpy.utils.logger import ComponentLogger, Logger, LoggerProtocol


class TestLoggerProtocol:
    """Tests for the LoggerProtocol."""

    def test_logger_protocol_with_logger_class(self):
        """Test that Logger class implements LoggerProtocol."""
        logger = Logger()
        assert isinstance(logger, LoggerProtocol)

    def test_logger_protocol_with_component_logger(self):
        """Test that ComponentLogger implements LoggerProtocol."""
        base_logger = Logger()
        component_logger = ComponentLogger(base_logger, "TestComponent")
        assert isinstance(component_logger, LoggerProtocol)

    def test_logger_protocol_with_mock(self):
        """Test that a mock with required methods implements LoggerProtocol."""
        mock_logger = Mock()
        mock_logger.debug = Mock()
        mock_logger.info = Mock()
        mock_logger.warning = Mock()
        mock_logger.error = Mock()
        mock_logger.critical = Mock()

        assert isinstance(mock_logger, LoggerProtocol)


class TestComponentLogger:
    """Tests for the ComponentLogger class."""

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing."""
        mock = Mock(spec=LoggerProtocol)
        return mock

    @pytest.fixture
    def component_logger(self, mock_logger):
        """Create a ComponentLogger instance for testing."""
        return ComponentLogger(mock_logger, "TestComponent")

    def test_init(self, mock_logger):
        """Test ComponentLogger initialization."""
        component_logger = ComponentLogger(mock_logger, "TestComponent")

        assert component_logger._logger == mock_logger
        assert component_logger._component_name == "TestComponent"

    def test_add_component_context(self, component_logger):
        """Test _add_component_context method."""
        message = "Test message"
        kwargs = {"key1": "value1", "key2": "value2"}

        prefixed_message, updated_kwargs = component_logger._add_component_context(
            message, **kwargs
        )

        assert prefixed_message == "[TestComponent] Test message"
        assert updated_kwargs["component"] == "TestComponent"
        assert updated_kwargs["key1"] == "value1"
        assert updated_kwargs["key2"] == "value2"

    def test_debug(self, component_logger, mock_logger):
        """Test debug logging with component identification."""
        component_logger.debug("Debug message", extra="data")

        mock_logger.debug.assert_called_once_with(
            "[TestComponent] Debug message", extra="data", component="TestComponent"
        )

    def test_info(self, component_logger, mock_logger):
        """Test info logging with component identification."""
        component_logger.info("Info message", extra="data")

        mock_logger.info.assert_called_once_with(
            "[TestComponent] Info message", extra="data", component="TestComponent"
        )

    def test_warning(self, component_logger, mock_logger):
        """Test warning logging with component identification."""
        component_logger.warning("Warning message", extra="data")

        mock_logger.warning.assert_called_once_with(
            "[TestComponent] Warning message", extra="data", component="TestComponent"
        )

    def test_error(self, component_logger, mock_logger):
        """Test error logging with component identification."""
        component_logger.error("Error message", extra="data")

        mock_logger.error.assert_called_once_with(
            "[TestComponent] Error message", extra="data", component="TestComponent"
        )

    def test_critical(self, component_logger, mock_logger):
        """Test critical logging with component identification."""
        component_logger.critical("Critical message", extra="data")

        mock_logger.critical.assert_called_once_with(
            "[TestComponent] Critical message", extra="data", component="TestComponent"
        )

    def test_all_log_levels_with_no_kwargs(self, component_logger, mock_logger):
        """Test all log levels work without additional kwargs."""
        component_logger.debug("Debug")
        component_logger.info("Info")
        component_logger.warning("Warning")
        component_logger.error("Error")
        component_logger.critical("Critical")

        mock_logger.debug.assert_called_once_with(
            "[TestComponent] Debug", component="TestComponent"
        )
        mock_logger.info.assert_called_once_with("[TestComponent] Info", component="TestComponent")
        mock_logger.warning.assert_called_once_with(
            "[TestComponent] Warning", component="TestComponent"
        )
        mock_logger.error.assert_called_once_with(
            "[TestComponent] Error", component="TestComponent"
        )
        mock_logger.critical.assert_called_once_with(
            "[TestComponent] Critical", component="TestComponent"
        )


class TestLogger:
    """Tests for the Logger class."""

    def test_init_default_values(self):
        """Test Logger initialization with default values."""
        logger = Logger()

        assert logger.logger.name == "grpy-request-client"
        assert logger.logger.level == logging.INFO
        assert len(logger.logger.handlers) == 1  # Console handler
        assert isinstance(logger.logger.handlers[0], logging.StreamHandler)

    def test_init_custom_values(self):
        """Test Logger initialization with custom values."""
        logger = Logger(name="custom-logger", level=logging.DEBUG, log_to_console=False)

        assert logger.logger.name == "custom-logger"
        assert logger.logger.level == logging.DEBUG
        assert len(logger.logger.handlers) == 0  # No console handler

    def test_init_with_file_handler(self, tmp_path):
        """Test Logger initialization with file handler."""
        log_file = tmp_path / "test.log"
        logger = Logger(log_file=str(log_file))

        assert len(logger.logger.handlers) == 2  # Console + file handler
        file_handler = next(h for h in logger.logger.handlers if isinstance(h, logging.FileHandler))
        assert file_handler.baseFilename == str(log_file)

    def test_log_levels_constants(self):
        """Test that log level constants are properly set."""
        assert Logger.DEBUG == logging.DEBUG
        assert Logger.INFO == logging.INFO
        assert Logger.WARNING == logging.WARNING
        assert Logger.ERROR == logging.ERROR
        assert Logger.CRITICAL == logging.CRITICAL

    def test_get_component_logger(self):
        """Test get_component_logger method."""
        logger = Logger()
        component_logger = logger.get_component_logger("TestComponent")

        assert isinstance(component_logger, ComponentLogger)
        assert component_logger._logger == logger
        assert component_logger._component_name == "TestComponent"

    @patch("sys.stdout", new_callable=StringIO)
    def test_debug_logging(self, mock_stdout):
        """Test debug logging functionality."""
        logger = Logger(level=logging.DEBUG)
        logger.debug("Debug message", key="value")

        output = mock_stdout.getvalue()
        assert "DEBUG" in output
        assert "Debug message - key=value" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_info_logging(self, mock_stdout):
        """Test info logging functionality."""
        logger = Logger()
        logger.info("Info message", key="value")

        output = mock_stdout.getvalue()
        assert "INFO" in output
        assert "Info message - key=value" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_warning_logging(self, mock_stdout):
        """Test warning logging functionality."""
        logger = Logger()
        logger.warning("Warning message", key="value")

        output = mock_stdout.getvalue()
        assert "WARNING" in output
        assert "Warning message - key=value" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_error_logging(self, mock_stdout):
        """Test error logging functionality."""
        logger = Logger()
        logger.error("Error message", key="value")

        output = mock_stdout.getvalue()
        assert "ERROR" in output
        assert "Error message - key=value" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_critical_logging(self, mock_stdout):
        """Test critical logging functionality."""
        logger = Logger()
        logger.critical("Critical message", key="value")

        output = mock_stdout.getvalue()
        assert "CRITICAL" in output
        assert "Critical message - key=value" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_logging_with_multiple_kwargs(self, mock_stdout):
        """Test logging with multiple kwargs."""
        logger = Logger()
        logger.info("Message", key1="value1", key2="value2", key3="value3")

        output = mock_stdout.getvalue()
        assert "INFO" in output
        assert "Message - " in output
        assert "key1=value1" in output
        assert "key2=value2" in output
        assert "key3=value3" in output

    def test_log_level_filtering(self):
        """Test that log level filtering works correctly."""
        # Capture logs to test filtering
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            logger = Logger(level=logging.WARNING)

            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")

            output = mock_stdout.getvalue()

            # Only warning should appear
            assert "Debug message" not in output
            assert "Info message" not in output
            assert "Warning message" in output

    def test_handlers_cleared_on_init(self):
        """Test that existing handlers are cleared during initialization."""
        # Create a logger with a handler
        test_logger = logging.getLogger("test-clear-handlers")
        test_logger.addHandler(logging.StreamHandler())
        initial_handler_count = len(test_logger.handlers)

        # Initialize our Logger class with the same name
        logger = Logger(name="test-clear-handlers")

        # Should have cleared existing handlers and added new ones
        assert len(logger.logger.handlers) == 1  # Only our console handler
        assert initial_handler_count >= 1  # Had at least one handler before

    def test_file_logging(self, tmp_path):
        """Test logging to file."""
        log_file = tmp_path / "test.log"
        logger = Logger(log_file=str(log_file), log_to_console=False)

        logger.info("Test file message", key="value")

        # Read the log file
        with open(log_file, "r") as f:
            content = f.read()

        assert "INFO" in content
        assert "Test file message - key=value" in content

    def test_both_console_and_file_logging(self, tmp_path):
        """Test logging to both console and file."""
        log_file = tmp_path / "test.log"

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            logger = Logger(log_file=str(log_file), log_to_console=True)
            logger.info("Test message")

            # Check console output
            console_output = mock_stdout.getvalue()
            assert "Test message" in console_output

        # Check file output
        with open(log_file, "r") as f:
            file_content = f.read()
        assert "Test message" in file_content


class TestLoggerIntegration:
    """Integration tests for logger components working together."""

    @patch("sys.stdout", new_callable=StringIO)
    def test_logger_with_component_logger_integration(self, mock_stdout):
        """Test Logger and ComponentLogger working together."""
        base_logger = Logger(level=logging.DEBUG)
        component_logger = base_logger.get_component_logger("IntegrationTest")

        component_logger.info("Integration test message", test_key="test_value")

        output = mock_stdout.getvalue()
        assert "INFO" in output
        assert "[IntegrationTest] Integration test message" in output
        assert "test_key=test_value" in output
        assert "component=IntegrationTest" in output

    def test_multiple_component_loggers_same_base(self):
        """Test multiple ComponentLoggers using the same base logger."""
        base_logger = Logger()
        component1 = base_logger.get_component_logger("Component1")
        component2 = base_logger.get_component_logger("Component2")

        assert component1._logger == base_logger
        assert component2._logger == base_logger
        assert component1._component_name == "Component1"
        assert component2._component_name == "Component2"
        assert component1 != component2

    @patch("sys.stdout", new_callable=StringIO)
    def test_different_components_different_output(self, mock_stdout):
        """Test that different components produce distinguishable output."""
        base_logger = Logger()
        component1 = base_logger.get_component_logger("Component1")
        component2 = base_logger.get_component_logger("Component2")

        component1.info("Message from component 1")
        component2.error("Message from component 2")

        output = mock_stdout.getvalue()
        assert "[Component1] Message from component 1" in output
        assert "[Component2] Message from component 2" in output
        assert "component=Component1" in output
        assert "component=Component2" in output
