from typing import Type, Callable, Dict, Iterator

from .file_format import FileFormat
from .image_file_format import ImageFileFormat


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
    def convertable_to() -> Dict[Type["FileFormat"], Callable[[], Iterator["FileFormat"]]]:
        from ..converters.pdf_to_jpeg import PdfToJpeg
        return {
            ImageFileFormat: PdfToJpeg.convert
        }
