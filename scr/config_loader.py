import json

class ConfigLoader:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_file_path, 'r') as config_file:
            config = json.load(config_file)
        return config

    def get_config(self):
        return self.config
