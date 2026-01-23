"""
Retriever Utilities - Helper functions cho retrieval operations.
"""
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore


def format_retrieved_docs(
    docs: List[Document],
    max_length: Optional[int] = None,
) -> str:
    """
    Format retrieved documents thành context string.
    
    Args:
        docs: List of retrieved documents
        max_length: Maximum length of formatted string (None for no limit)
        
    Returns:
        Formatted context string
    """
    if not docs:
        return ""
    
    context_parts = []
    total_length = 0
    
    for doc in docs:
        content = doc.page_content
        if max_length and total_length + len(content) > max_length:
            # Truncate last document if needed
            remaining = max_length - total_length
            if remaining > 0:
                context_parts.append(content[:remaining])
            break
        
        context_parts.append(content)
        total_length += len(content)
    
    return "\n\n---\n\n".join(context_parts)


def extract_metadata(
    docs: List[Document],
    key: str,
    default: Any = None,
) -> List[Any]:
    """
    Extract metadata values từ documents.
    
    Args:
        docs: List of documents
        key: Metadata key to extract
        default: Default value if key not found
        
    Returns:
        List of metadata values
    """
    return [doc.metadata.get(key, default) for doc in docs if doc.metadata]


def filter_docs_by_metadata(
    docs: List[Document],
    metadata_filter: Dict[str, Any],
) -> List[Document]:
    """
    Filter documents by metadata.
    
    Args:
        docs: List of documents
        metadata_filter: Dictionary of metadata key-value pairs to filter by
        
    Returns:
        Filtered list of documents
    """
    filtered = []
    for doc in docs:
        match = True
        for key, value in metadata_filter.items():
            if doc.metadata.get(key) != value:
                match = False
                break
        if match:
            filtered.append(doc)
    return filtered

