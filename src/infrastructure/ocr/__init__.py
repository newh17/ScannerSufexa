"""
Módulo de OCR y procesamiento de documentos.
"""

from .pdf_processor import PDFProcessor
from .tesseract_ocr_service import TesseractOCRService

__all__ = [
    "PDFProcessor",
    "TesseractOCRService",
]
