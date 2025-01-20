import os
import tempfile
import time

import ollama

from text_extract_api.extract.strategies.strategy import Strategy
from text_extract_api.files.file_formats.file_format import FileFormat
from text_extract_api.files.file_formats.image import ImageFileFormat


class MiniCPMVStrategy(Strategy):
    """MiniCPM-V OCR Strategy"""

    @classmethod
    def name(cls) -> str:
        return "minicpm_v"

    def extract_text(self, file_format: FileFormat, language: str = 'en') -> str:

        if (
                not isinstance(file_format, ImageFileFormat)
                and not file_format.can_convert_to(ImageFileFormat)
        ):
            raise TypeError(
                f"MiniCPM-V - format {file_format.mime_type} is not supported (yet?)"
            )

        images = FileFormat.convert_to(file_format, ImageFileFormat)
        extracted_text = ""
        start_time = time.time()
        ocr_percent_done = 0
        num_pages = len(images)
        for i, image in enumerate(images):

            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                temp_file.write(image.binary)
                temp_filename = temp_file.name

            # Generate text using the Llama 3.2 Vision model
            try:
                response = ollama.chat("minicpm-v", [{
                    'role': 'user',
                    'content': os.getenv('MINICPMV_PROMPT', "You are OCR. Convert image to markdown."),
                    'images': [temp_filename]
                }], stream=True)
                os.remove(temp_filename)
                num_chunk = 1
                for chunk in response:
                    meta = {
                        'progress': str(30 + ocr_percent_done),
                        'status': 'OCR Processing'
                                  + '(page ' + str(i + 1) + ' of ' + str(num_pages) + ')'
                                  + ' chunk no: ' + str(num_chunk),
                        'start_time': start_time,
                        'elapsed_time': time.time() - start_time}
                    self.update_state_callback(state='PROGRESS', meta=meta)
                    num_chunk += 1
                    extracted_text += chunk['message']['content']

                ocr_percent_done += int(
                    20 / num_pages)  # 20% of work is for OCR - just a stupid assumption from tasks.py
            except ollama.ResponseError as e:
                print('Error:', e.error)
                raise Exception("Failed to generate text with MiniCPM-V model")

            print(response)

        return extracted_text
