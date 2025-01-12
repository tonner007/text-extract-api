from marker.convert import convert_single_pdf
from marker.models import load_all_models

from text_extract_api.extract.ocr_strategies.ocr_strategy import OCRStrategy
from text_extract_api.files.file_formats.file_format import FileFormat


class MarkerOCRStrategy(OCRStrategy):

    @classmethod
    def name(cls) -> str:
        return "marker"

    def extract_text(self, file: FileFormat):
        model_lst = load_all_models()
        full_text, images, out_meta = convert_single_pdf(file.binary, model_lst)
        return full_text
