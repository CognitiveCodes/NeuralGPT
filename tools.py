import os

class Tools:
    def __init__(self):
        pass

    def create_directory(self, directory_path):
        os.makedirs(directory_path, exist_ok=True)

    def modify_file(self, file_path, modification_function):
        with open(file_path, 'r') as f:
            data = f.read()
        modified_data = modification_function(data)
        with open(file_path, 'w') as f:
            f.write(modified_data)