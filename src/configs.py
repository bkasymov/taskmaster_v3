import logging

import yaml

from parser import load_config, validate_config
from process import Process




def reload_config(shell, file_path):
    new_config = load_config(file_path)

    if not validate_config(new_config):
        print("Reload failed: configuration validation failed. Check the logs for details.")
        return

    for name, details in new_config.items():
        if name in shell.processes:
            shell.processes[name].config = details
        else:
            shell.processes[name] = Process(name, details)
    print("Configuration reloaded.")

def setup_logging():
    logging.basicConfig(filename='taskmaster.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
