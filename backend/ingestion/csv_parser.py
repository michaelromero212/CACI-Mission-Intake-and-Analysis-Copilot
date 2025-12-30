"""
CSV parser - converts CSV files into normalized text format.
"""
import csv
from io import StringIO
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def parse_csv(file_content: bytes, filename: str = "unknown.csv") -> Dict[str, Any]:
    """
    Parse CSV file and convert to structured text.
    
    Args:
        file_content: Raw bytes of the CSV file
        filename: Original filename for logging
        
    Returns:
        Dict containing extracted data, text representation, and any errors
    """
    result = {
        "text": "",
        "metadata": {},
        "rows": [],
        "headers": [],
        "row_count": 0,
        "errors": []
    }
    
    try:
        # Decode bytes to string
        content_str = file_content.decode('utf-8')
        csv_file = StringIO(content_str)
        
        # Detect dialect
        try:
            dialect = csv.Sniffer().sniff(content_str[:1024])
        except csv.Error:
            dialect = csv.excel
        
        csv_file.seek(0)
        reader = csv.reader(csv_file, dialect)
        
        # Extract headers
        headers = next(reader, [])
        result["headers"] = headers
        
        # Extract rows
        rows = []
        for row in reader:
            if any(cell.strip() for cell in row):  # Skip empty rows
                rows.append(row)
        
        result["rows"] = rows
        result["row_count"] = len(rows)
        result["metadata"] = {
            "column_count": len(headers),
            "row_count": len(rows),
            "columns": headers
        }
        
        # Convert to readable text format
        text_parts = []
        text_parts.append(f"CSV Data Summary: {len(rows)} rows, {len(headers)} columns")
        text_parts.append(f"Columns: {', '.join(headers)}")
        text_parts.append("")
        
        # Include row contents
        for i, row in enumerate(rows[:50]):  # Limit to first 50 rows for processing
            row_text = " | ".join(f"{headers[j] if j < len(headers) else 'Col'+str(j)}: {cell}" 
                                   for j, cell in enumerate(row))
            text_parts.append(f"Row {i + 1}: {row_text}")
        
        if len(rows) > 50:
            text_parts.append(f"... and {len(rows) - 50} more rows")
        
        result["text"] = "\n".join(text_parts)
        
    except UnicodeDecodeError as e:
        error_msg = f"Failed to decode CSV (encoding issue): {str(e)}"
        result["errors"].append(error_msg)
        logger.error(f"[{filename}] {error_msg}")
    except Exception as e:
        error_msg = f"Failed to parse CSV: {str(e)}"
        result["errors"].append(error_msg)
        logger.error(f"[{filename}] {error_msg}")
    
    return result
