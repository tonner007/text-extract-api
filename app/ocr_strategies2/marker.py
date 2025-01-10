from marker.convert import convert_single_pdf
from marker.models import load_all_models

from extract.ocr_strategies.ocr_strategy import OCRStrategy

class MarkerOCRStrategy(OCRStrategy):
    """Marker OCR Strategy"""
    def extract_text_from_pdf(self, file_bytes):
        model_lst = load_all_models()
        full_text, images, out_meta = convert_single_pdf(file_bytes, model_lst)
        return full_text
