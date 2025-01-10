from typing import Type

from extract import FileFormat
from extract import ImageProcessor

class ImageFileFormat(FileFormat):
    @staticmethod
    def accepted_mime_types() -> list[str]:
        return ["image/jpeg", "image/png", "image/bmp", "image/gif", "image/tiff"]

    @staticmethod
    def is_pageable() -> bool:
        return False


    @classmethod
    def default_iterator_file_format(cls) -> Type["ImageFileFormat"]:
        return cls

    def unify(self) -> "FileFormat":
        unified_image = ImageProcessor.unify_image(self.to_binary, ImageFormat.JPEG)
        return ImageFileFormat.from_binary(unified_image, self.filename, self.mime_type)
