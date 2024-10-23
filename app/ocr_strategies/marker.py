import marker
from ocr_strategies.ocr_strategy import OCRStrategy

class MarkerOCRStrategy(OCRStrategy):
    """Marker OCR Strategy"""
    def extract_text_from_pdf(self, pdf_bytes):
        return marker.convert_single_pdf(pdf_bytes)

