from files.file_formats.file_format import FileFormat
from files.file_formats.image_file_format import ImageFileFormat
from ocr_strategies.ocr_strategy import OCRStrategy
import ollama
import os
import time
import base64
import tempfile
from pdf2image import convert_from_bytes

class LlamaVisionOCRStrategy(OCRStrategy):
    """Llama 3.2 Vision OCR Strategy"""

    def extract_text_from_pdf(self, pdf_bytes):
        # Convert PDF bytes to images
        images = convert_from_bytes(pdf_bytes)
        extracted_text = ""
        start_time = time.time()
        ocr_percent_done = 0
        num_pages = len(images)
        for i, image in enumerate(images):
            # Convert image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            # img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            # Save image to a temporary file and get its path
            temp_filename = None
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                image.save(temp_file, format="JPEG")
                temp_filename = temp_file.name

            # Generate text using the Llama 3.2 Vision model
            try:
                response = ollama.chat("llama3.2-vision", [{
                    'role': 'user',
                    'content': os.getenv('LLAMA_VISION_PROMPT', "You are OCR. Convert image to markdown."),
                    'images': [temp_filename]
                }], stream=True)
                os.remove(temp_filename)
                num_chunk = 1
                for chunk in response:
                    self.update_state_callback(state='PROGRESS', meta={'progress': str(30 + ocr_percent_done),
                                                                       'status': 'OCR Processing (page ' + str(
                                                                           i + 1) + ' of ' + str(
                                                                           num_pages) + ') chunk no: ' + str(num_chunk),
                                                                       'start_time': start_time,
                                                                       'elapsed_time': time.time() - start_time})  # Example progress update
                    num_chunk += 1
                    extracted_text += chunk['message']['content']

                ocr_percent_done += int(
                    20 / num_pages)  # 20% of work is for OCR - just a stupid assumption from tasks.py
            except ollama.ResponseError as e:
                print('Error:', e.error)
                raise Exception("Failed to generate text with Llama 3.2 Vision model")

            print(response)
            #page_text = response.get("response", "")
            #extracted_text += f"--- Page {i + 1} ---\n{page_text}\n"

        return extracted_text

    def extract_text(self, file_format: FileFormat):

        if file_format.convertable_to(ImageFileFormat):
            raise Exception(f"Llama Vision does not handle files of mime type: {file_format.mime_type}")

        images = list(FileFormat.convert_to(file_format, ImageFileFormat));

        extracted_text = ""
        start_time = time.time()
        ocr_percent_done = 0
        num_pages = len(images)
        for i, image in enumerate(images):
            img_str = image.unify(image).to_base64();

            # Generate text using the Llama 3.2 Vision model
            try:
                response = ollama.chat("llama3.2-vision", [{
                    'content': os.getenv('LLAMA_VISION_PROMPT', "You are OCR. Convert image to markdown."),
                    'images': [img_str]
                }], stream=True)
                num_chunk = 1
                for chunk in response:
                    self.update_state_callback(state='PROGRESS', meta={'progress': str(30 + ocr_percent_done),
                                                                       'status': 'OCR Processing (page ' + str(
                                                                           i + 1) + ' of ' + str(
                                                                           num_pages) + ') chunk no: ' + str(num_chunk),
                                                                       'start_time': start_time,
                                                                       'elapsed_time': time.time() - start_time})  # Example progress update
                    num_chunk += 1
                    extracted_text += chunk['message']['content']

                ocr_percent_done += int(
                    20 / num_pages)  # 20% of work is for OCR - just a stupid assumption from tasks.py
            except ollama.ResponseError as e:
                print('Error:', e.error)
                raise Exception("Failed to generate text with Llama 3.2 Vision model")

            print(response)
            # page_text = response.get("response", "")
            # extracted_text += f"--- Page {i + 1} ---\n{page_text}\n"

        return extracted_text
