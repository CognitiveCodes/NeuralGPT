import os
from typing import List

class DocumentEditor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_type = os.path.splitext(file_path)[1]
        self.file_content = self._read_file()

    def _read_file(self):
        with open(self.file_path, 'r') as f:
            return f.read()

    def _write_file(self):
        with open(self.file_path, 'w') as f:
            f.write(self.file_content)

    def insert_text(self, text: str, position: int):
        self.file_content = self.file_content[:position] + text + self.file_content[position:]
        self._write_file()

    def delete_text(self, start: int, end: int):
        self.file_content = self.file_content[:start] + self.file_content[end:]
        self._write_file()

    def format_text(self, start: int, end: int, format_type: str):
        # Implement text formatting (bold, italic, underline, etc.)
        pass

    def insert_image(self, image_path: str, position: int):
        # Implement image insertion
        pass

    def insert_hyperlink(self, link: str, position: int):
        # Implement hyperlink insertion
        pass

    def get_file_content(self):
        return self.file_content

class DocumentEditorManager:
    def __init__(self):
        self.editors = {}

    def create_editor(self, file_path: str) -> str:
        editor_id = str(len(self.editors))
        self.editors[editor_id] = DocumentEditor(file_path)
        return editor_id

    def delete_editor(self, editor_id: str):
        del self.editors[editor_id]

    def get_editor(self, editor_id: str) -> DocumentEditor:
        return self.editors[editor_id]

    def get_all_editors(self) -> List[DocumentEditor]:
        return list(self.editors.values())