"""
AssignMind — PDF Parser Tests
"""

import pytest
from app.utils.pdf_parser import (
    extract_document_text,
    DocumentParserError,
    sanitize_extracted_text
)

def test_sanitize_extracted_text():
    # Regular text is fine
    assert "Hello World" in sanitize_extracted_text("Hello World")
    
    # Strip scripts
    assert "alert" not in sanitize_extracted_text("Normal <script>alert(1)</script> text")
    
    # Basic SQLi dropping
    assert "DROP TABLE" not in sanitize_extracted_text("Some regular DROP TABLE users;")

def test_extract_txt_valid():
    content = b"This is a valid text file with enough characters to pass the minimum fifty length check validation."
    result = extract_document_text("test.txt", content)
    assert result == "This is a valid text file with enough characters to pass the minimum fifty length check validation."

def test_extract_empty_file():
    with pytest.raises(DocumentParserError, match="File is empty"):
        extract_document_text("test.txt", b"")

def test_extract_too_short():
    with pytest.raises(DocumentParserError, match="Extracted text is too short or empty"):
        extract_document_text("test.txt", b"too short")

def test_extract_oversized():
    # 10 MB + 1
    content = b"a" * (10 * 1024 * 1024 + 1)
    with pytest.raises(DocumentParserError, match="File exceeds 10 MB"):
        extract_document_text("test.txt", content)

def test_invalid_extension():
    with pytest.raises(DocumentParserError, match="Unsupported file format"):
        extract_document_text("test.png", b"fake png file payload long enough to pass limits if it was a text document format.")
