import magic
from typing import Optional


def guess_mime_type(binary_data: Optional[bytes] = None, filename: Optional[str] = None) -> str:
    mime = magic.Magic(mime=True)
    if binary_data:
        return mime.from_buffer(binary_data)
    if filename:
        return mime.from_file(filename)
    raise ValueError("Either binary_data or filename must be provided to guess the MIME type.")

