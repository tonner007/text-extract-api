class AcceptedFormat:
    """
    Base class for accepted file formats.
    Each specific format should extend this class and implement the required methods.
    """

    def accepts(self, mime_type: str) -> bool:
        raise NotImplementedError("Subclasses must implement this method")

    def get_default_filename(self) -> str:
        raise NotImplementedError("Subclasses must implement this method")

    def get_suggested_prompt(self) -> str:
        raise NotImplementedError("Subclasses must implement this method")

    def get_format_info(self) -> dict:
        raise NotImplementedError("Subclasses must implement this method")

    def unify(self, file_content: bytes) -> list[bytes]:
        """
        Converts the file to a universal format.
        Default implementation returns the file content wrapped in a list.

        :param file_content: File content in bytes.
        :return: A list containing the unified file content in bytes.
        """
        return [file_content]

    def convertable_to(self) -> dict:
        """
        Defines what formats this file type can be converted to.
        Returns a dictionary where keys are target formats and values are converter functions.

        :return: A dictionary of convertible formats and their converters.
        """
        return {}

    def convert(self, target_format: str, file_content: bytes) -> list[bytes]:
        """
        Converts the file to the target format.

        :param target_format: Desired target format.
        :param file_content: File content in bytes.
        :return: A list of files in the target format as bytes.
        """
        converters = self.convertable_to()
        if target_format not in converters:
            raise ValueError(f"Cannot convert to {target_format}.")
        return converters[target_format](file_content)
