class OCRStrategy:
    """Base OCR Strategy Interface"""
    def extract_text_from_pdf(self, pdf_bytes):
        raise NotImplementedError("Subclasses must implement this method")
