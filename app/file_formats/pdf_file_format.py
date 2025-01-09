from typing import Type

from file_formats.file_format import FileFormat
from file_formats.image_file_format import ImageFileFormat


class PdfFileFormat(FileFormat):
    @staticmethod
    def accepted_mime_types() -> list[str]:
        return ["application/pdf"]

    @staticmethod
    def is_pageable() -> bool:
        return True

    @classmethod
    def default_iterator_file_format(cls) -> Type[ImageFileFormat]:
        return ImageFileFormat

    @staticmethod
    def convertable_to() -> dict[str, callable]:
        """
        Defines formats that a PDF can be converted to.
        Provides a mapping of target formats and their corresponding converters.
        """
        from file_formats.converters.pdf_to_jpeg_converter import PdfToJpegConverter

        return {
            "image/jpeg": lambda pdf: PdfToJpegConverter.convert_to_list(pdf)
        }
