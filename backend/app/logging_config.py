"""
Logging configuration for the AI Pakistan Travel Guide API

Provides structured logging with appropriate levels:
- INFO: Normal flow, request processing
- WARNING: Degraded data, missing optional features
- ERROR: Failures requiring attention
"""
import logging
import sys
from datetime import datetime


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure and return the main application logger.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    # Create formatter with timestamp, level, and message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Get the root logger for the app
    logger = logging.getLogger("travel_safety_api")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = "travel_safety_api") -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically module name)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"travel_safety_api.{name}")


# Pre-configured loggers for different components
class Loggers:
    """Container for component-specific loggers"""
    
    @staticmethod
    def api() -> logging.Logger:
        """Logger for API endpoints"""
        return get_logger("api")
    
    @staticmethod
    def ai() -> logging.Logger:
        """Logger for AI/LLM operations"""
        return get_logger("ai")
    
    @staticmethod
    def weather() -> logging.Logger:
        """Logger for weather service"""
        return get_logger("weather")
    
    @staticmethod
    def routes() -> logging.Logger:
        """Logger for route service"""
        return get_logger("routes")
    
    @staticmethod
    def safety() -> logging.Logger:
        """Logger for safety service"""
        return get_logger("safety")
    
    @staticmethod
    def database() -> logging.Logger:
        """Logger for database operations"""
        return get_logger("database")
