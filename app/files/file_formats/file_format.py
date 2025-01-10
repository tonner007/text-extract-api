import base64
from hashlib import md5
from typing import Type, Iterator, Optional, Dict, Callable, Union, TypeVar
from extract import guess_mime_type

T = TypeVar("T", bound="FileFormat")

class FileFormat:
    default_filename = None
    default_mime_type = None

    def __init__(self, binary_file_content: bytes, filename: str, mime_type: str):

        if not binary_file_content:
            raise ValueError("binary_file_content cannot be empty")

        if filename is None:
            if FileFormat.default_filename is None:
                raise ValueError("filename cannot be empty, as no default is set")
            filename = FileFormat.default_filename

        if mime_type is None:
            if FileFormat.default_mime_type is None:
                raise ValueError("mime_type cannot be empty, as no default is set")
            mime_type = FileFormat.default_mime_type

        self._binary_file_content = binary_file_content
        self._filename = filename
        self._mime_type = mime_type

    @property
    def to_base64(self) -> str:
        """Encodes the given file content to a Base64 string."""
        return base64.b64encode(self._binary_file_content).decode('utf-8')

    @property
    def to_hash(self) -> str:
        return md5(self.to_binary).hexdigest()

    @property
    def to_binary(self) -> bytes:
        return self._binary_file_content

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def mime_type(self) -> str:
        return self._mime_type

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
    def default_iterator_file_format(cls) -> Type["FileFormat"]:
        """
        Returns the default format for iterating over the file.
        """
        if not cls.is_pageable():
            return cls
        raise NotImplementedError("Pageable formats must implement default_iterator_file_format.")

    @classmethod
    def accept_mime_type(cls, mime_type: str) -> bool:
        """
        Checks if the given MIME type is accepted by this format.
        """
        return mime_type in cls.accepted_mime_types()

    @staticmethod
    def convertable_to() -> Dict[Type["FileFormat"], Callable[[], Iterator["FileFormat"]]]:
        """
        Defines what formats this file type can be converted to.
        Returns a dictionary where keys are target formats and values are functions
        that produce FileFormat instances.

        :return: A dictionary of convertible formats and their converters.
        """
        return {}

    def convert_to(self, target_format: Type[T]) -> Iterator[T]:
        # @todo check if this compare is ok
        if self.__class__ == target_format:
            yield self
        converters = self.convertable_to()
        if target_format not in converters:
            raise ValueError(f"Cannot convert to {target_format}. Conversion not supported.")
        return converters[target_format]()

    @classmethod
    def from_base64(cls, base64_string: str, filename: str, mime_type: str) -> Type[FileFormat]:
        try:
            decoded_content = base64.b64decode(base64_string)
        except (base64.binascii.Error, ValueError):
            raise ValueError("Invalid Base64-encoded input.")
        return cls.from_binary(binary=decoded_content, filename=filename, mime_type=mime_type)

    @classmethod
    def from_binary(cls, binary: bytes, filename: str, mime_type: str) -> FileFormat:
        if mime_type is None:
            mime_type = guess_mime_type(binary_data=binary, filename=filename)

        return cls(binary_file_content=binary, filename=filename, mime_type=mime_type)

    @classmethod
    def create(data: Union[bytes, str], filename: Optional[str] = None) -> FileFormat:
        if isinstance(data, str):
            binary_data = base64.b64decode(data)
        else:
            binary_data = data

        mime_type = guess_mime_type(binary_data=binary_data, filename=filename)
        file_format_class = get_file_format_class(mime_type)
        return file_format_class(binary_file_content=binary_data, filename=filename or "unknown", mime_type=mime_type)

    @classmethod
    def get_format_info(cls) -> dict:
        """
        Returns information about the format, including accepted MIME types, pageable status, and convertible formats.
        """
        return {
            "mime_types": cls.accepted_mime_types(),
            "pageable": cls.is_pageable(),
            "convertable_to": cls.convertable_to()
        }

    def get_iterator(self, target_format: Optional["FileFormat"]) -> Iterator["FileFormat"]:
        """
        Returns an iterator over the file content in the specified format.

        :param target_format: The desired format for the output. Defaults to the subclass-defined default format.
        :return: Iterator of FileFormat instances.
        """
        final_format = target_format or self.default_iterator_file_format

        if self.is_pageable():
            if final_format.is_pageable():
                raise ValueError("Target format and current format are both pageable. Cannot iterate.")
            else:
                yield self.convert_to(final_format)
        else:
            yield self.convert_to(final_format)

    def unify(self) -> "FileFormat":
        """
        Converts the file to a universal type for that format (e.g., JPEG from png, bmp, tiff, etc.).
        Default implementation returns a new instance of the current format.

        :return: Unified format as a new self instance.
        """
        return self

    @staticmethod
    def get_file_format_class(mime_type: str) -> Type["FileFormat"]:
        for subclass in FileFormat.__subclasses__():
            if mime_type in subclass.accepted_mime_types():
                return subclass
        raise ValueError(f"No matching FileFormat class for MIME type: {mime_type}")

    @staticmethod
    def _create_file_format(data: Union[bytes, str], filename: Optional[str] = None) -> FileFormat:
        if isinstance(data, str):
            binary_data = base64.b64decode(data)
        else:
            binary_data = data

        mime_type = guess_mime_type(binary_data=binary_data, filename=filename)
        file_format_class = FileFormat.get_file_format_class(mime_type)
        return file_format_class(binary_file_content=binary_data, filename=filename or "unknown", mime_type=mime_type)
