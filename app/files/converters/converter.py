from typing import Iterator, List

from .. import FileFormat


class Converter:
    @staticmethod
    def convert(file_format: FileFormat) -> Iterator[FileFormat]:
        raise NotImplementedError("Subclasses must implement the `convert` method.")

    @classmethod
    def convert_to_list(cls, file_format: FileFormat) -> List[FileFormat]:
        return list(cls.convert(file_format))

    @classmethod
    def convert_force_single(cls, file_format: FileFormat) -> FileFormat:
        """ Warning - this will return only first page """
        return next(cls.convert(file_format), None)
