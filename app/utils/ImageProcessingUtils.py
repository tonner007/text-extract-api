from enum import Enum
from PIL import Image
from io import BytesIO
import base64

class ImageFormat(Enum):
    JPEG = "JPEG"
    PNG = "PNG"
    BMP = "BMP"
    TIFF = "TIFF"

class ImageProcessingUtils:
    @staticmethod
    def unify_image(image_bytes: bytes, target_format: ImageFormat ="JPEG", convert_to_rgb: bool=True) -> bytes:
        """
        Prepares an image for OCR by unifying its format and color mode.
        - Converts image to the desired format (e.g., JPEG).
        - Converts grayscale, CMYK, etc., to RGB (if required).
        :param image_bytes: Input image in bytes.
        :param target_format: Desired format for the output image (default: JPEG)
        :param convert_to_rgb: Convert to RGB format if not already (default: True).
        :return:Image bytes in the new format.
        """
        image = Image.open(BytesIO(image_bytes))

        # We need RGB - problem occurred when P (png) was sent
        if convert_to_rgb and image.mode != "RGB":
            image = image.convert("RGB")

        # Save the image in the target format
        buffered = BytesIO()
        image.save(buffered, format=target_format.value)
        return buffered.getvalue()

    @staticmethod
    def encode_image_to_base64(image_bytes: bytes):
        """
        Encodes  image bytes to a base64 string for OCR services that require it.
        :param image_bytes: Input image in bytes.
        :return: Base64-encoded string of the image.
        """
        return base64.b64encode(image_bytes).decode("utf-8")

    @staticmethod
    def unify_image_to_base64(image_byes: bytes):
        unified_image = ImageProcessingUtils.unify_image(image_byes)
        return ImageProcessingUtils.encode_image_to_base64(unified_image)

