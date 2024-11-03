import yaml

class YamlParser:
    def __init__(self, file_path: str):
        self._file_path = file_path
    
    def read_config_file(self):
        with open(self._file_path) as file:
            data = yaml.safe_load(file)
        return data