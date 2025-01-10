from typing import Type, Callable, Dict, Iterator

from extract import PdfToJpeg
from extract import FileFormat
from extract import ImageFileFormat


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
        return {
            ImageFileFormat: PdfToJpeg.convert
        }
