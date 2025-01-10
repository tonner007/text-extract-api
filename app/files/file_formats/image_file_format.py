from enum import Enum
from typing import Type

from .file_format import FileFormat


class ImageSupportedExportFormats(Enum):
    JPEG = "JPEG"
    PNG = "PNG"
    BMP = "BMP"
    TIFF = "TIFF"


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
        from ..utils.image_processor import ImageProcessor
        unified_image = ImageProcessor.unify_image(self.to_binary, ImageSupportedExportFormats.JPEG)
        return ImageFileFormat.from_binary(unified_image, self.filename, self.mime_type)
