from typing import Type

from files.file_formats.file_format import FileFormat
from utils.image_processor import ImageProcessor, ImageFormat

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

