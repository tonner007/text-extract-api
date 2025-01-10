from io import BytesIO

from PIL import Image

from ..file_formats.image_file_format import ImageSupportedExportFormats


class ImageProcessor:
    @staticmethod
    def unify_image(image_bytes: bytes, target_format: ImageSupportedExportFormats = "JPEG",
                    convert_to_rgb: bool = True) -> bytes:
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
