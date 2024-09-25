from spectre.file_handlers.BaseFileHandler import BaseFileHandler

class TextHandler(BaseFileHandler):
    def __init__(self, parent_path: str, base_file_name: str, **kwargs):
        super().__init__(parent_path, base_file_name, extension = "txt", **kwargs)
        return 
    
    def read(self) -> dict:
        with open(self.file_path, 'r') as f:
            return f.read()