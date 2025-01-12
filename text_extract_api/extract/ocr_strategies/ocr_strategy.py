from __future__ import annotations

import importlib
import pkgutil
from typing import Type, Dict

from text_extract_api.files.file_formats.file_format import FileFormat


def discover_strategies() -> Dict[str, Type]:
    strategies = {}

    for module_info in pkgutil.iter_modules():
        if module_info.name.startswith("text_extract_api"):
            try:
                module = importlib.import_module(module_info.name)
            except ImportError:
                continue
            if hasattr(module, "__path__"):
                for submodule_info in pkgutil.walk_packages(module.__path__, module_info.name + "."):
                    if ".ocr_strategies." in submodule_info.name:
                        try:
                            ocr_module = importlib.import_module(submodule_info.name)
                        except ImportError:
                            continue
                        for attr_name in dir(ocr_module):
                            attr = getattr(ocr_module, attr_name)
                            if isinstance(attr, type) and issubclass(attr, OCRStrategy) and attr is not OCRStrategy:
                                strategies[attr.name()] = attr()

    return strategies


class OCRStrategy:
    _strategies: Dict[str, Type] = {}

    def __init__(self):
        self.update_state_callback = None

    def set_update_state_callback(self, callback):
        self.update_state_callback = callback

    def update_state(self, state, meta):
        if self.update_state_callback:
            self.update_state_callback(state, meta)

    @classmethod
    def name(cls) -> str:
        raise NotImplementedError("Strategy subclasses must implement name")

    @classmethod
    def extract_text(cls, file_format: Type["FileFormat"]):
        raise NotImplementedError("Strategy subclasses must implement extract_text method")

    @classmethod
    def get_strategy(cls, name: str) -> Type["OCRStrategy"]:
        """
        Fetches and returns a registered strategy class based on the given name.

        Args:
            name: The name of the strategy to fetch.

        Returns:
            The strategy class corresponding to the provided name.

        Raises:
            ValueError: If the specified strategy name does not exist among the registered strategies.
        """

        if name not in cls._strategies:
            cls.autodiscover_strategies()
            if name not in cls._strategies:
                available = ', '.join(cls._strategies.keys())
                raise ValueError(f"Unknown strategy '{name}'. Available: {available}")

        return cls._strategies[name]

    @classmethod
    def autodiscover_strategies(cls):
        cls._strategies = discover_strategies()
