import argparse
import logging
import sys

import yaml



from ProcessManager import ProcessManager

filename = None
all_processes = {}
def read_config_file(config):
    try:
        with open(config, 'r') as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        print("Error in config file:", str(e))
        logging.error("Error in config file")
        sys.exit(-1)


def validate_config(filename):
    if not (filename.endswith('.yml') or filename.endswith('.yaml')):
        print("Error in config file: not a YAML file")
        logging.error("Error in config file: not a YAML file")
        sys.exit(-1)

    config_data = read_config_file(filename)
    for data_key, config in config_data.items():
        if "command" not in config or not isinstance(config["command"], str):
            error_message = f"Error in config file: command not found or not a string in {data_key}"
            print(error_message)
            logging.error(error_message)
            raise ValueError(error_message)

def parse_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="config_file.yaml")
    args = parser.parse_args()
    filename = args.config
    validate_config(filename)
    text_config = read_config_file(filename)
    print(text_config)
    return text_config


