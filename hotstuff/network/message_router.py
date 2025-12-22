"""
MessageRouter for routing messages to protocol handlers.

Routes incoming messages to the appropriate handler based on message type.
"""

from typing import Dict
from typing import Callable
from typing import List

from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.domain.models.messages.base_message import BaseMessage
from hotstuff.logging_config.logger import StructuredLogger


MessageHandler = Callable[[BaseMessage], List]


class MessageRouter:
    """
    Routes messages to registered handlers based on type.
    
    Each message type can have exactly one handler registered.
    """
    
    def __init__(self):
        """Initialize the message router."""
        self._handlers: Dict[MessageType, MessageHandler] = {}
        self._logger = StructuredLogger.get_logger("router")
    
    def register_handler(
        self,
        message_type: MessageType,
        handler: MessageHandler
    ) -> None:
        """
        Register a handler for a message type.
        
        Args:
            message_type: Type of message to handle.
            handler: Handler function to call.
        """
        self._handlers[message_type] = handler
        self._logger.debug(f"Registered handler for {message_type.name}")
    
    def route(self, message: BaseMessage) -> List:
        """
        Route a message to its registered handler.
        
        Args:
            message: The message to route.
            
        Returns:
            Result from the handler, or empty list if no handler.
        """
        handler = self._handlers.get(message.message_type)
        if handler is None:
            self._logger.warning(f"No handler for message type {message.message_type.name}")
            return []
        
        return handler(message)
    
    def has_handler(self, message_type: MessageType) -> bool:
        """Check if a handler is registered for a message type."""
        return message_type in self._handlers
    
    def clear_handlers(self) -> None:
        """Remove all registered handlers."""
        self._handlers.clear()
