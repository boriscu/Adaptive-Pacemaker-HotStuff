"""
Base exception class for HotStuff.

All custom exceptions inherit from HotStuffException.
"""


class HotStuffException(Exception):
    """
    Base exception class for all HotStuff-related errors.
    
    Provides structured error messages with optional context.
    """
    
    def __init__(self, message: str, context: dict = None):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message.
            context: Optional dictionary with additional context.
        """
        self.message = message
        self.context = context or {}
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format the error message with context."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} [{context_str}]"
        return self.message
