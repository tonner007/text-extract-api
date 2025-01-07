import base64
from ocr_strategies.ocr_strategy import OCRStrategy
import ollama
from io import BytesIO
import os
import time
from PIL import Image


class LlamaVisionOCRStrategy(OCRStrategy):
    """Llama 3.2 Vision OCR Strategy"""

    def extract_text_from_png(self, image_bytes):
        # Convert PDF bytes to images
        print(f"Using llama strategy")

        image = Image.open(BytesIO(image_bytes))

        extracted_text = ""
        start_time = time.time()
        ocr_percent_done = 0
        num_pages = 1
#         for i, image in enumerate(images):
            # Convert image to base64
        buffered = BytesIO()
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
            print(response)
        except ollama.ResponseError as e:
            print('Error:', e.error)
            raise Exception("Failed to generate text with Llama 3.2 Vision model")

            #page_text = response.get("response", "")
            #extracted_text += f"--- Page {i + 1} ---\n{page_text}\n"

        return extracted_text
