import os
import yaml

class StorageStrategy:
    def __init__(self, context):
        self.context = context

    def save(self, file_name, dest_file_name, content):
        raise NotImplementedError("Subclasses must implement this method")

    def load(self, file_name):
        raise NotImplementedError("Subclasses must implement this method")

    def list(self):
        raise NotImplementedError("Subclasses must implement this method")

    def delete(self, file_name):
        raise NotImplementedError("Subclasses must implement this method")