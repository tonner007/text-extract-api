from typing import Type, List, Callable, Dict

from files.converters.pdf_to_jpeg import PdfToJpeg
from files.file_formats.file_format import FileFormat
from files.file_formats.image_file_format import ImageFileFormat


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
    def convertable_to() -> Dict[Type["FileFormat"], Callable[[], List["FileFormat"]]]:
        return {
            ImageFileFormat: PdfToJpeg.convert
        }
