from file_formats.file_format import FileFormat

class ImageFileFormat(FileFormat):
    @staticmethod
    def accepted_mime_types() -> list[str]:
        return ["image/jpeg", "image/png", "image/bmp", "image/gif", "image/tiff"]

    @staticmethod
    def is_pageable() -> bool:
        return False

    @classmethod
    def default_iterator_file_format(cls) -> "ImageFileFormat":
        return cls
