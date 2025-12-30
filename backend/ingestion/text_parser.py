"""
Text parser - processes raw text input with basic cleaning.
"""
import re
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def parse_text(content: str, source_label: str = "text_input") -> Dict[str, Any]:
    """
    Process raw text input with basic normalization.
    
    Args:
        content: Raw text content
        source_label: Label for the text source
        
    Returns:
        Dict containing cleaned text and metadata
    """
    result = {
        "text": "",
        "metadata": {},
        "errors": []
    }
    
    try:
        # Basic cleaning
        cleaned = content.strip()
        
        # Normalize whitespace
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)  # Max 2 newlines
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)  # Normalize spaces
        
        # Calculate basic stats
        word_count = len(cleaned.split())
        char_count = len(cleaned)
        line_count = cleaned.count('\n') + 1 if cleaned else 0
        
        result["text"] = cleaned
        result["metadata"] = {
            "word_count": word_count,
            "character_count": char_count,
            "line_count": line_count,
            "source_label": source_label
        }
        
        if not cleaned:
            result["errors"].append("Empty text content provided")
            
    except Exception as e:
        error_msg = f"Failed to process text: {str(e)}"
        result["errors"].append(error_msg)
        logger.error(f"[{source_label}] {error_msg}")
    
    return result
