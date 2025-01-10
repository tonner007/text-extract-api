import cv2
import numpy as np
import pytesseract

from app.files import FileFormat
from app.files import ImageFileFormat
from .ocr_strategy import OCRStrategy


class TesseractOCRStrategy(OCRStrategy):
    """Tesseract OCR Strategy"""

    def extract_text(self, file_format: FileFormat):

        if file_format.convertable_to(ImageFileFormat):
            raise Exception(f"TesseractOCRStrategy does not handle files of mime type: {file_format.mime_type}")

        images = list(FileFormat.convert_to(file_format, ImageFileFormat));
        extracted_text = ""

        for i, image in enumerate(images):
            rgb_image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
            page_text = pytesseract.image_to_string(rgb_image)
            extracted_text += f"--- Page {i + 1} ---\n{page_text}\n"

        return extracted_text
