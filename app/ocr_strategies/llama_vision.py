import base64
from ocr_strategies.ocr_strategy import OCRStrategy
import ollama
import io
import os
import time
from pdf2image import convert_from_bytes
import base64
from PIL import Image
from io import BytesIO
from utils import ImageProcessingUtils


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
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

            # Generate text using the Llama 3.2 Vision model
            try:
                response = ollama.chat("llama3.2-vision", [{
                    'content':  os.getenv('LLAMA_VISION_PROMPT', "You are OCR. Convert image to markdown."),
                    'images': [img_str]
                }], stream=True)
                num_chunk = 1
                for chunk in response:
                    self.update_state_callback(state='PROGRESS', meta={'progress': str(30 + ocr_percent_done), 'status': 'OCR Processing (page ' + str(i+1) + ' of ' + str(num_pages) +') chunk no: ' + str(num_chunk), 'start_time': start_time, 'elapsed_time': time.time() - start_time})  # Example progress update
                    num_chunk += 1
                    extracted_text += chunk['message']['content']

                ocr_percent_done += int(20/num_pages) #20% of work is for OCR - just a stupid assumption from tasks.py
            except ollama.ResponseError as e:
                print('Error:', e.error)
                raise Exception("Failed to generate text with Llama 3.2 Vision model")

            print(response) 
            #page_text = response.get("response", "")
            #extracted_text += f"--- Page {i + 1} ---\n{page_text}\n"

        return extracted_text


    def extract_text_from_image(self, image_bytes):

        unified_image = ImageProcessingUtils.unify_image(image_bytes, target_format="JPEG")
        img_str = ImageProcessingUtils.encode_image_to_base64(unified_image)

        extracted_text = ""
        start_time = time.time()

        try:
            response = ollama.chat(
                "llama3.2-vision",
                [
                    {
                        "content": os.getenv(
                            "LLAMA_VISION_PROMPT", "You are OCR. Convert image to markdown."
                        ),
                        "images": [img_str],
                    }
                ],
                stream=True,
            )

            num_chunk = 1
            for chunk in response:
                self.update_state_callback(
                    state="PROGRESS",
                    meta={
                        "progress": "50",  # Example: static or calculated progress
                        "status": f"OCR Processing chunk {num_chunk}",
                        "start_time": start_time,
                        "elapsed_time": time.time() - start_time,
                    },
                )
                num_chunk += 1
                extracted_text += chunk["message"]["content"]

        except ollama.ResponseError as e:
            print("Error:", e.error)
            raise Exception("Failed to generate text with Llama 3.2 Vision model")

        return extracted_text
