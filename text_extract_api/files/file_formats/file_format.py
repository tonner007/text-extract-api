from __future__ import annotations

import base64
from hashlib import md5
from typing import Type, Iterator, Optional, Dict, Callable, Union, TypeVar

from text_extract_api.files.utils import filetype

T = TypeVar("T", bound="FileFormat")

class FileFormat:
    _default_filename: str =  ""
    _default_mime_type: str = ""
    _base64_cache: Optional[str] = None

    # Construction

    def __init__(self, binary_file_content: bytes, filename: Optional[str] = None, mime_type: Optional[str] = None):
        if not binary_file_content:
            raise ValueError("binary_file_content cannot be empty.")
        if not filename and not self._default_filename:
            filename='file'
        if not mime_type and not self._default_mime_type:
            raise ValueError(f"{self.__class__.__name__} don\'t allow empty mime type.")

        self._binary_file_content = binary_file_content
        self._filename = filename or self._default_filename
        self._mime_type = mime_type or self._default_mime_type

    @classmethod
    def from_base64(cls, base64_string: str, filename: Optional[str] = None, mime_type: Optional[str] = None) -> Type["FileFormat"]:
        binary = base64.b64decode(base64_string)
        instance = cls.from_binary(binary, filename=filename, mime_type=mime_type)
        instance._base64_cache = base64_string
        return instance

    @classmethod
    def from_binary(cls, binary: bytes, filename: Optional[str] = None, mime_type: Optional[str] = None) -> Type["FileFormat"]:
        mime_type = mime_type or filetype.guess_mime_type(binary_data=binary, filename=filename)
        file_format_class = cls._get_file_format_class(mime_type)
        return file_format_class(binary_file_content=binary, filename=filename, mime_type=mime_type)

    # Properties
    @property
    def filename(self) -> str:
        return self._filename

    @property
    def mime_type(self) -> str:
        return self._mime_type

    @property
    def base64(self) -> str:
        if self._base64_cache is None:
            self._base64_cache = base64.b64encode(self._binary_file_content).decode('utf-8')
        return self._base64_cache

    @property
    def hash(self) -> str:
        return md5(self.binary).hexdigest()

    @property
    def binary(self) -> bytes:
        return self._binary_file_content

    @property
    def iterator(self, target_format: Optional["FileFormat"]) -> Iterator["FileFormat"]:
        """
        Return an iterator of a file(s)

        By default, the iterator uses the format defined by `default_iterator_file_format()`.
        If a `target_format` is provided, it must be compatible and convertible using
        `convertible_to()`.

        Args:
            target_format (Optional[Type[FileFormat]]): The desired file format for conversion.

        Returns:
            Iterator[FileFormat]: An iterator for the specified or default file format.

        Raises:
            ValueError: If the target format is not compatible or convertible.
        """
        final_format = target_format or self.default_iterator_file_format

        if self.is_pageable():
            if final_format.is_pageable():
                raise ValueError("Target format and current format are both pageable. Cannot iterate.")
            else:
                yield self.convert_to(final_format)
        else:
            yield self.convert_to(final_format)


    # Utils
    @staticmethod
    def accepted_mime_types() -> list[str]:
        raise NotImplementedError("Subclasses must implement accepted_mime_types.")

    @staticmethod
    def is_pageable() -> bool:
        """
        Checks if the format supports pagination. Pdf does, image does not. :)
        """
        raise NotImplementedError("Subclasses must implement is_pageable.")

    def can_convert_to(self, target_format: Type["FileFormat"]) -> bool:
        convertible_keys = self.convertible_to().keys()
        return any(target_format is key for key in convertible_keys)

    def convert_to(self, target_format: Type["FileFormat"]) -> Iterator["FileFormat"]:
        if isinstance(self, target_format):
            yield self
        # @todo check if this compare is ok
        converters = self.convertible_to()
        if target_format not in converters:
            raise ValueError(f"Cannot convert to {target_format}. Conversion not supported.")

        return converters[target_format](self)

    @staticmethod
    def convertible_to() -> Dict[Type["FileFormat"], Callable[[Type["FileFormat"]], Iterator[Type["Converter"]]]]:
        """
        Defines what formats this file type can be converted to.
        Returns a dictionary where keys are target formats and values are functions
        that produce FileFormat instances.

        :return: A dictionary of convertible formats and their converters.
        """
        return {}

    def unify(self) -> Type["FileFormat"]:
        """
        Converts the file to a universal type for that format (e.g., JPEG from png, bmp, tiff, etc.).
        Default implementation returns a new instance of the current format.

        :return: Unified format as a new self instance.
        """
        return self

    @classmethod
    def default_iterator_file_format(cls) -> Type["FileFormat"]:
        if not cls.is_pageable():
            return cls
        raise NotImplementedError("Pageable formats must implement default_iterator_file_format.")

    def unify(self) -> Type["FileFormat"]:
        """
        Converts the file to a universal type for that format (e.g., JPEG from png, bmp, tiff, etc.).
        Default implementation returns a new instance of the current format.

        :return: Unified format as a new self instance.
        """
        return self

    @staticmethod
    def _get_file_format_class(mime_type: str) -> Type["FileFormat"]:
        for subclass in FileFormat.__subclasses__():
            if mime_type in subclass.accepted_mime_types():
                return subclass
        raise ValueError(f"No matching FileFormat class for mime type: {mime_type}")