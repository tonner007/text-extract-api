from typing import Iterator
from extract import BaseConverter
from pdf2image import convert_from_bytes

from extract import ImageFileFormat
from extract import PdfFileFormat


class PdfToJpeg(BaseConverter):

    @staticmethod
    def convert(file_format: PdfFileFormat) -> Iterator[ImageFileFormat]:
        pages = convert_from_bytes(file_format.to_binary)
        for i, page in enumerate(pages, start=1):
            yield ImageFileFormat.from_binary(
                binary=PdfToJpeg._image_to_bytes(page),
                filename=f"{file_format.filename}_page_{i}.jpg",
                mime_type="image/jpeg"
            )

    @staticmethod
    def _image_to_bytes(image) -> bytes:
        from io import BytesIO

        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        return buffer.getvalue()
