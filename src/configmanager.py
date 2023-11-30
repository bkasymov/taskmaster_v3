import argparse
import logging
import sys
import yaml
from processmanager import ProcessManager

class ConfigManager:
    def __init__(self):
        self.config_file = None
        self.config_data = None

        self.parse_args()
        self.parse_config()
    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("config", help="config_file.yaml")
        self.config_file = parser.parse_args().config

    def parse_config(self):
        self.validate_format()
        self.read_config_file()
        self.validate_config_data()
    def validate_format(self):
        if not (self.config_file.endswith('.yml') or self.config_file.endswith('.yaml')):
            print("Error in config file: not a YAML file")
            logging.error("Error in config file: not a YAML file")
            sys.exit(-1)

    def read_config_file(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config_data = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            print("Error in config file:", str(e))
            logging.error("Error in config file")
            sys.exit(-1)

    def validate_config_data(self):
        for data_key, config in self.config_data.items():
            if "command" not in config or not isinstance(config["command"], str):
                error_message = f"Error in config file: command not found or not a string in {data_key}"
                print(error_message)
                logging.error(error_message)
                raise ValueError(error_message)

    @staticmethod
    def generate_processes_from_data(config_data):
        all_processes = {}
        for process_name in config_data:
            process = ProcessManager(process_name, config_data[process_name])
            all_processes[process_name] = process
        return all_processes



