class OCRStrategy:

    def __init__(self):
        print("a")
        self.update_state_callback = None

    def set_update_state_callback(self, callback):
        self.update_state_callback = callback

    def update_state(self, state, meta):
        if self.update_state_callback:
            self.update_state_callback(state, meta)
                
    """Base OCR Strategy Interface"""
    def extract_text_from_pdf(self, pdf_bytes):
        raise NotImplementedError("Subclasses must implement this method")

    def extract_text_from_image(self, file_bytes):
        raise NotImplementedError("Subclasses must implement this method")