import base64
from ocr_strategies.ocr_strategy import OCRStrategy
import ollama
from io import BytesIO
import os
import time
from PIL import Image


class LlamaVisionOCRStrategy(OCRStrategy):
    """Llama 3.2 Vision OCR Strategy"""

    def extract_text_from_pdf(self, image_bytes):
        print("Using Llama Vision OCR Strategy")

        # Convert image bytes to PIL Image
        image = Image.open(BytesIO(image_bytes))
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Convert image to base64
        buffered = BytesIO()

        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Initialize extracted text and time tracking
        extracted_text = ""
        start_time = time.time()

        # Generate text using Llama 3.2 Vision model
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

            # Process response chunks
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
