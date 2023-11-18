import logging

import yaml

from process import Process


def initialize_processes(config):
    processes = {}
    for name, details in config.items():
        processes[name] = Process(name, details)
    return processes

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
def validate_config(config):
    """Проверяет конфигурацию на наличие обязательных ключей."""
    for name, details in config.items():
        if 'command' not in details:
            logging.error(f"Error: 'command' key is missing in the configuration of '{name}'.")
            return False
    return True