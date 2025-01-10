from typing import Optional, Type

import magic

from ..file_formats.file_format import FileFormat


def guess_mime_type(binary_data: Optional[bytes] = None, filename: Optional[str] = None) -> str:
    mime = magic.Magic(mime=True)
    if binary_data:
        return mime.from_buffer(binary_data)
    if filename:
        return mime.from_file(filename)
    raise ValueError("Either binary_data or filename must be provided to guess the MIME type.")


@staticmethod
def get_file_format_class(mime_type: str) -> Type["FileFormat"]:
    for subclass in FileFormat.__subclasses__():
        if mime_type in subclass.accepted_mime_types():
            return subclass
    raise ValueError(f"No matching FileFormat class for MIME type: {mime_type}")
