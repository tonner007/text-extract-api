import base64
from ocr_strategies.ocr_strategy import OCRStrategy
import ollama
import io
import os
from pdf2image import convert_from_bytes

class LlamaVisionOCRStrategy(OCRStrategy):
    """Llama 3.2 Vision OCR Strategy"""

    def extract_text_from_pdf(self, pdf_bytes):
        # Convert PDF bytes to images
        images = convert_from_bytes(pdf_bytes)
        extracted_text = ""

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
                for chunk in response:
                    extracted_text += chunk['message']['content']

            except ollama.ResponseError as e:
                print('Error:', e.error)
                raise Exception("Failed to generate text with Llama 3.2 Vision model")

            print(response) 
            #page_text = response.get("response", "")
            #extracted_text += f"--- Page {i + 1} ---\n{page_text}\n"

        return extracted_text