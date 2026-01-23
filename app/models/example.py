"""
Example Domain Models - Mẫu domain models.

Domain models đại diện cho business entities và có thể chứa business logic.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Conversation:
    """
    Domain model cho conversation.
    
    Attributes:
        id: Conversation ID
        user_id: User ID
        messages: List of messages
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    id: str
    user_id: str
    messages: list
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    def add_message(self, message: dict) -> None:
        """Add message to conversation."""
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_message_count(self) -> int:
        """Get total message count."""
        return len(self.messages)

