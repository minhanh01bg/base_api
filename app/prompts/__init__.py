"""
Prompts module - Chứa các prompt templates cho graph nodes.
"""

from .intent_classification import INTENT_CLASSIFICATION_PROMPT
from .extract_file_info import EXTRACT_FILE_INFO_PROMPT

__all__ = [
    "INTENT_CLASSIFICATION_PROMPT",
    "EXTRACT_FILE_INFO_PROMPT",
]

