import os
from storage_strategies.storage_strategy import StorageStrategy
from datetime import datetime
from pathlib import Path

def resolve_path(path):
    # Expand `~` to the home directory
    expanded_path = os.path.expanduser(path)
    # Convert to absolute path, resolving any `..` or `.`
    absolute_path = os.path.abspath(expanded_path)
    return absolute_path

class LocalFilesystemStorageStrategy(StorageStrategy):
    def __init__(self, context):
        super().__init__(context)
        self.base_directory = resolve_path(self.context['settings']['root_path'])
        print("Storage base directory: ", self.base_directory)
        self.create_subfolders = self.context['settings'].get('create_subfolders', False)
        self.subfolder_names_format = self.context['settings'].get('subfolder_names_format', '')
        os.makedirs(self.base_directory, exist_ok=True)

    def _get_subfolder_path(self, file_name):
        if not self.subfolder_names_format:
            return self.base_directory
        
        now = datetime.now()
        subfolder_path = self.subfolder_names_format.format(
            file_name=file_name,
            Y=now.strftime('%Y'),
            mm=now.strftime('%m'),
            dd=now.strftime('%d'),
            HH=now.strftime('%H'),
            MM=now.strftime('%M'),
            SS=now.strftime('%S')
        )
        return os.path.join(self.base_directory, subfolder_path)

    def save(self, file_name, dest_file_name, content):
        file_name = dest_file_name.format(file_fullname=file_name,  # file_name with path
                                     file_name=Path(file_name).stem,  # file_name without path
                                     file_extension = Path(file_name).suffix,   # file extension
                                     Y=datetime.now().strftime('%Y'),
                                     mm=datetime.now().strftime('%m'),
                                     dd=datetime.now().strftime('%d'),
                                     HH=datetime.now().strftime('%H'),
                                     MM=datetime.now().strftime('%M'),
                                     SS=datetime.now().strftime('%S'))
        subfolder_path = self._get_subfolder_path(file_name)
        full_path = os.path.join(subfolder_path, file_name)
        full_directory = os.path.dirname(full_path)
        os.makedirs(full_directory, exist_ok=True)
        with open(full_path, 'w') as file:
            file.write(content)

    def load(self, file_name):
        subfolder_path = self._get_subfolder_path(file_name)
        file_path = os.path.join(subfolder_path, file_name)
        with open(file_path, 'r') as file:
            return file.read()

    def list(self):
        return os.listdir(self.base_directory)

    def delete(self, file_name):
        subfolder_path = self._get_subfolder_path(file_name)
        file_path = os.path.join(subfolder_path, file_name)
        os.remove(file_path)