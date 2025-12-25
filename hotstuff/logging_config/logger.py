"""
Structured logging setup for HotStuff simulation.

Provides consistent logging format and configuration.
"""

import logging
import sys


class StructuredLogger:
    """
    Factory for creating structured loggers.

    Provides consistent formatting and log level configuration
    across all modules in the HotStuff simulation.
    """

    _configured: bool = False
    _log_level: int = logging.INFO

    @classmethod
    def configure(cls, log_level: str = "INFO") -> None:
        """
        Configure the logging system.

        Args:
            log_level: Log level as string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        """
        if cls._configured:
            return

        level = getattr(logging, log_level.upper(), logging.INFO)
        cls._log_level = level

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        handler.setLevel(level)

        root_logger = logging.getLogger("hotstuff")
        root_logger.setLevel(level)
        root_logger.addHandler(handler)
        root_logger.propagate = False

        cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger for the specified module.

        Args:
            name: Name of the module/component requesting a logger.

        Returns:
            Configured Logger instance.
        """
        if not cls._configured:
            cls.configure()

        return logging.getLogger(f"hotstuff.{name}")

    @classmethod
    def reset(cls) -> None:
        """Reset logging configuration (primarily for testing)."""
        cls._configured = False
        logger = logging.getLogger("hotstuff")
        logger.handlers.clear()
