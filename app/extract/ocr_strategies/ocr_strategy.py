
class OCRStrategy:

    def __init__(self):
        print("a")
        self.update_state_callback = None

    def set_update_state_callback(self, callback):
        self.update_state_callback = callback

    def update_state(self, state, meta):
        if self.update_state_callback:
            self.update_state_callback(state, meta)
                
    def extract_text_from_pdf(self, pdf_bytes):
        # Leave for backward compatibility
        self.extract_text(PdfFileFormat.from_binary(pdf_bytes))

    """Base OCR Strategy Interface"""
    def extract_text(self, file_format: FileFormat):
        raise NotImplementedError("Subclasses must implement this method")