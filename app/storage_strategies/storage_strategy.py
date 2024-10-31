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
    
    def format_file_name(self, file_name, format_string):
        return format_string.format(file_fullname=file_name,  # file_name with path
                                file_name=os.path.basename(file_name),  # file_name without path
                                file_extension = os.path.splitext(file_name)[1],   # file extension
                                Y=os.path.basename(file_name).split('.')[0],
                                mm=os.path.basename(file_name).split('.')[1],
                                dd=os.path.basename(file_name).split('.')[2],
                                HH=os.path.basename(file_name).split('.')[3],
                                MM=os.path.basename(file_name).split('.')[4],
                                SS=os.path.basename(file_name).split('.')[5])