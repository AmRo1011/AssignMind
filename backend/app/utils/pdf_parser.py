"""
AssignMind — PDF Parser & Text Extractor

Handles extraction of raw text from user uploaded files (.txt, .pdf).
Implements fallbacks for scanned PDFs using OCR, validates size and length,
and utilizes strict sanitation (Constitution §III).
"""

import io
import re
import structlog
from typing import BinaryIO

import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from langdetect import detect, LangDetectException

from app.utils.sanitize import sanitize_and_trim

logger = structlog.get_logger()

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MIN_TEXT_LENGTH = 50

class DocumentParserError(Exception):
    """Exception raised when a document fails strict format or parsing rules."""
    pass


def sanitize_extracted_text(text: str) -> str:
    """
    Remove potentially dangerous script tags or SQL fragments.
    Extracting raw assignment text means we only want standard words.
    """
    # Extra protection against embedded scripts or common SQLi vectors first
    text = re.sub(r"(?is)<script[^>]*>.*?</script>", "", text)
    text = re.sub(r"(?i)<\/?script[^>]*>", "", text)
    text = re.sub(r"(?i)(SELECT|INSERT|UPDATE|DELETE|DROP|UNION)(\s+.*)?;?", "", text)
    
    # Use standard bleacher/sanitizer to handle HTML tag removal
    return sanitize_and_trim(text, max_length=100000)


def extract_document_text(filename: str, content: bytes) -> str:
    """
    Parse document bytes (PDF or Text), extract sanitized text.
    Rejects sizes > 10MB or lengths < 50 chars.
    """
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise DocumentParserError("File exceeds 10 MB size limit.")
        
    if len(content) == 0:
        raise DocumentParserError("File is empty.")

    extracted_text = ""
    ext = filename.lower().split('.')[-1]
    
    if ext == "txt":
        extracted_text = _extract_txt(content)
    elif ext == "pdf":
        extracted_text = _extract_pdf(content)
        if not extracted_text.strip():
            extracted_text = _extract_pdf_ocr(content)
    else:
        raise DocumentParserError("Unsupported file format. Please upload PDF or TXT.")

    final_text = sanitize_extracted_text(extracted_text)
    
    if len(final_text) < MIN_TEXT_LENGTH:
        raise DocumentParserError("Extracted text is too short or empty. Must be at least 50 chars.")
        
    try:
        detect(final_text) 
    except LangDetectException:
        raise DocumentParserError("Could not determine language of document.")
        
    return final_text


def _extract_txt(content: bytes) -> str:
    try:
        return content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return content.decode('latin-1')
        except Exception:
            raise DocumentParserError("Text file must be valid UTF-8.")


def _extract_pdf(content: bytes) -> str:
    """Extract standard text from a PDF without OCR."""
    try:
        text_frames = []
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_frames.append(page_text)
        return "\n".join(text_frames)
    except Exception as e:
        logger.warning("pdf_standard_extract_failed", error=str(e))
        return ""


def _extract_pdf_ocr(content: bytes) -> str:
    """OCR fallback for scanned PDFs."""
    try:
        images = convert_from_bytes(content)
        texts = []
        for img in images:
            texts.append(pytesseract.image_to_string(img))
        return "\n".join(texts)
    except Exception as e:
        logger.warning("pdf_ocr_failed", error=str(e))
        raise DocumentParserError(
            "This appears to be a scanned PDF, but OCR failed or is unavailable. "
            "Please upload a standard text-based PDF or plain text file."
        )
