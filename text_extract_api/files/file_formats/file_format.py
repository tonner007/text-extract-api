import base64
from hashlib import md5
from typing import Type, Iterator, Optional, Dict, Callable, List
import magic


class FileFormat:
    _default_filename: str = ""
    _default_mime_type: str = ""
    _base64_cache: Optional[str] = None
    _binary_file_content = None
    _filename = None
    _mime_type = None

    # Construction

    def __init__(self, _binary_file_content: bytes, _filename: Optional[str] = None, _mime_type: Optional[str] = None):
        print(_binary_file_content)
        """
        Attributes:
            _binary_file_content (bytes): The binary content of the file.
            _filename (str): The name of the file. Defaults to a predefined
                value if not provided.
            _mime_type (str): The MIME type of the file. Defaults to a
                predefined value if not provided.

        Parameters:
            _binary_file_content: The binary content of the file.
            _filename: The name of the file. Defaults to None.
            _mime_type: The MIME type. Defaults to None.

        Raises:
            ValueError: If binary_file_content is empty or if no MIME type
                is provided or defaulted to.
        """
        if not _binary_file_content:
            raise ValueError("binary_file_content cannot be empty.")
        if not _filename and not self._default_filename:
            _filename = 'file'
        if not _mime_type and not self._default_mime_type:
            raise ValueError(f"{self.__class__.__name__} don\'t allow empty mime type.")

        self._filename = _filename or self._default_filename
        self._mime_type = _mime_type or self._default_mime_type

    @classmethod
    def from_base64(cls, base64_string: str, filename: Optional[str] = None, mime_type: Optional[str] = None) -> Type[
        "FileFormat"]:
        binary = base64.b64decode(base64_string)
        instance = cls.from_binary(binary, filename=filename, mime_type=mime_type)
        instance._base64_cache = base64_string
        return instance

    @classmethod
    def from_binary(cls, binary: bytes, filename: Optional[str] = None, mime_type: Optional[str] = None) -> Type[
        "FileFormat"]:
        mime_type = mime_type or FileFormat._guess_mime_type(binary_data=binary, filename=filename)
        from text_extract_api.files.file_formats.pdf_file_format import PdfFileFormat
        file_format_class = cls._get_file_format_class(mime_type)
        print(file_format_class)
        return file_format_class(_binary_file_content=binary, _filename=filename, _mime_type=mime_type)

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
        return md5(self._binary_file_content).hexdigest()

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

    def can_convert_to(self, target_format: FileFormat) -> bool:
        convertible_keys = self.convertible_to().keys()
        return any(target_format is key for key in convertible_keys)

    def convert_to(self, target_format: FileFormat) -> List["FileFormat"]:
        if isinstance(self, target_format):
            return [self];

        converters = self.convertible_to()
        if target_format not in converters:
            raise ValueError(f"Cannot convert to {target_format}. Conversion not supported.")

        return list(converters[target_format](self))

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
        import text_extract_api.files.file_formats.pdf_file_format  # noqa - its not unused import @todo autodiscover
        import text_extract_api.files.file_formats.image_file_format  # noqa - its not unused import @todo autodiscover
        for subclass in FileFormat.__subclasses__():
            if mime_type in subclass.accepted_mime_types():
                return subclass
        raise ValueError(f"No matching FileFormat class for mime type: {mime_type}")

    @staticmethod
    def _guess_mime_type(binary_data: Optional[bytes] = None, filename: Optional[str] = None) -> str:
        mime = magic.Magic(mime=True)
        if binary_data:
            return mime.from_buffer(binary_data)
        if filename:
            return mime.from_file(filename)
        raise ValueError("Either binary_data or filename must be provided to guess the MIME type.")


class FileField:
    def __init__(self, value: str):
        # Validate using FileFormat.from_base64
        self._file_format = FileFormat.from_base64(value)
        self.value = value

    def __str__(self) -> str:
        return self.value
