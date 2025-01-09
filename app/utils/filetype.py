import base64
import magic
from typing import Union, Optional
from files.file_formats.file_format import FileFormat


def guess_mime_type(binary_data: Optional[bytes] = None, filename: Optional[str] = None) -> str:
    mime = magic.Magic(mime=True)
    if binary_data:
        return mime.from_buffer(binary_data)
    if filename:
        return mime.from_file(filename)
    raise ValueError("Either binary_data or filename must be provided to guess the MIME type.")


def create_file_format(data: Union[bytes, str], filename: Optional[str] = None) -> FileFormat:
    if isinstance(data, str):
        binary_data = base64.b64decode(data)
    else:
        binary_data = data

    mime_type = guess_mime_type(binary_data=binary_data, filename=filename)
    file_format_class = get_file_format_class(mime_type)
    return file_format_class(binary_file_content=binary_data, filename=filename or "unknown", mime_type=mime_type)