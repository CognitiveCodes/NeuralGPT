import os
from typing import List

class FileProcessor:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path

    def upload_file(self, file_path: str, file_name: str) -> str:
        """
        Uploads a file to the storage_path and returns the URL where it can be accessed.
        """
        file_url = os.path.join(self.storage_path, file_name)
        with open(file_url, 'wb') as f:
            f.write(file_path.read())
        return file_url

    def download_file(self, file_url: str) -> bytes:
        """
        Downloads a file from the storage_path and returns its contents as bytes.
        """
        with open(file_url, 'rb') as f:
            file_contents = f.read()
        return file_contents

    def process_files(self, file_urls: List[str]) -> List[str]:
        """
        Processes a list of files specified by their URLs and returns a list of processed files' URLs.
        """
        processed_files = []
        for file_url in file_urls:
            # process file here
            processed_file_url = file_url + '_processed'
            processed_files.append(processed_file_url)
        return processed_files