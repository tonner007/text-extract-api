from typing import Type, Iterator, Optional
import base64

class FileFormat:
    def __init__(self, binary_file_content: bytes, filename: str, mime_type: str):
        if not binary_file_content:
            raise ValueError("file_content cannot be empty")
        if not filename:
            raise ValueError("filename cannot be empty")
        if not mime_type:
            raise ValueError("mime_type cannot be empty")

        self._binary_file_content = binary_file_content
        self._filename = filename
        self._mime_type = mime_type

    @property
    def base64(self) -> str:
        """Encodes the given file content to a Base64 string."""
        return base64.b64encode(self._binary_file_content).decode('utf-8')

    @property
    def file_content(self) -> bytes:
        return self._binary_file_content

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def mime_type(self) -> str:
        return self._mime_type

    # Methods to implement
    @staticmethod
    def accepted_mime_types() -> list[str]:
        raise NotImplementedError("Subclasses must implement accepted_mime_types.")

    @staticmethod
    def is_pageable() -> bool:
        """
        Checks if the format supports pagination. Pdf does, image does not. :)
        """
        raise NotImplementedError("Subclasses must implement is_pageable.")

    @classmethod
    def default_iterator_file_format(cls) -> "FileFormat":
        """
        Returns the default format for iterating over the file.
        """
        if not cls.is_pageable():
            return cls
        raise NotImplementedError("Pageable formats must implement default_iterator_file_format.")

    # Remaining methods
    @classmethod
    def accept_mime_type(cls, mime_type: str) -> bool:
        """
        Checks if the given MIME type is accepted by this format.
        """
        return mime_type in cls.accepted_mime_types()

    @staticmethod
    def convertable_to() -> dict[str, callable]:
        """
        Defines what formats this file type can be converted to.
        Returns a dictionary where keys are target formats and values are functions
        that produce FileFormat instances.

        :return: A dictionary of convertible formats and their converters.
        """
        return {}

    def convert_to(self, target_format: Type["FileFormat"]) -> ["FileFormat"]:
        converters = self.convertable_to()
        if target_format not in converters:
            raise ValueError(f"Cannot convert to {target_format}. Conversion not supported.")
        return converters[target_format]()

    @staticmethod
    def from_base64(base64_string: str, filename: str, mime_type: str) -> "FileFormat":
        try:
            decoded_content = base64.b64decode(base64_string)
        except (base64.binascii.Error, ValueError):
            raise ValueError("Invalid Base64-encoded input.")
        return FileFormat(binary_file_content=decoded_content, filename=filename, mime_type=mime_type)

    @staticmethod
    def from_binary(binary: bytes, filename: str, mime_type: str) -> "FileFormat":
        return FileFormat(binary_file_content=binary, filename=filename, mime_type=mime_type)

    @staticmethod
    def get_format_info(self) -> dict:
        """
        Returns information about the format, including accepted MIME types, pageable status, and convertible formats.
        """
        return {
            "mime_types": self.accepted_mime_types(),
            "pageable": self.is_pageable(),
            "convertable_to": self.convertable_to()
        }

    def get_iterator(self, target_format: Optional["FileFormat"]) -> Iterator["FileFormat"]:
        """
        Returns an iterator over the file content in the specified format.

        :param target_format: The desired format for the output. Defaults to the subclass-defined default format.
        :return: Iterator of FileFormat instances.
        """
        final_format = target_format or self.default_iterator_file_format

        if self.is_pageable:
            for page in self.get_pages():
                yield page.convert(final_format)
        else:
            yield self.convert(final_format)

    def unify(self) -> "FileFormat":
        """
        Converts the file to a universal type for that format (e.g., JPEG from png, bmp, tiff, etc.).
        Default implementation returns a new instance of the current format.

        :return: Unified format as a new self instance.
        """
        return self
