"""
PDF parser - extracts text and metadata from PDF files.
"""
from pypdf import PdfReader
from io import BytesIO
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def parse_pdf(file_content: bytes, filename: str = "unknown.pdf") -> Dict[str, Any]:
    """
    Extract text and metadata from a PDF file.
    
    Args:
        file_content: Raw bytes of the PDF file
        filename: Original filename for logging
        
    Returns:
        Dict containing extracted text, metadata, and any errors
    """
    result = {
        "text": "",
        "metadata": {},
        "page_count": 0,
        "errors": []
    }
    
    try:
        pdf_file = BytesIO(file_content)
        reader = PdfReader(pdf_file)
        
        # Extract metadata
        if reader.metadata:
            result["metadata"] = {
                "title": reader.metadata.get("/Title", ""),
                "author": reader.metadata.get("/Author", ""),
                "subject": reader.metadata.get("/Subject", ""),
                "creator": reader.metadata.get("/Creator", ""),
            }
        
        result["page_count"] = len(reader.pages)
        
        # Extract text from all pages
        text_parts = []
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            except Exception as e:
                error_msg = f"Error extracting page {i + 1}: {str(e)}"
                result["errors"].append(error_msg)
                logger.warning(f"[{filename}] {error_msg}")
        
        result["text"] = "\n\n".join(text_parts)
        
        if not result["text"].strip():
            result["errors"].append("No text content extracted from PDF")
            
    except Exception as e:
        error_msg = f"Failed to parse PDF: {str(e)}"
        result["errors"].append(error_msg)
        logger.error(f"[{filename}] {error_msg}")
    
    return result
