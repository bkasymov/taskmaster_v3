import argparse

from exceptions import ParseError
from logger import Logger
import logging
import os
import sys
import yaml
from params_validation import PARAMS_CONSTANTS, _no_check, _to_list

LOGLEVELCONSTANT = getattr(logging, os.environ.get('LOGLEVEL', 'INFO'), logging.INFO)

REQUIRED_PARAMS = ['cmd',]
class DaemonParser:
    def __init__(self, config_path):
        self.config_path = config_path
        self.logger = Logger(level=LOGLEVELCONSTANT)

        if not os.path.exists(self.config_path):
            print('')
            self.logger.error("Config file not found %s" % self.config_path)
            sys.exit(-1)

        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.load(f, Loader=yaml.FullLoader)
            self.logger.debug("Config file loaded")
        except Exception as e:
            self.logger.error("Error parsing config file: {}".format(e))
            sys.exit(-1)

        if 'programs' not in self.config:
            self.logger.error("Config file must contain `programs` section")
            sys.exit(-1)
        self.check_configuration()


    def check_configuration(self):
        programs = self.config.get('programs', {})

        if not programs:
            self.config['programs'] = {}
            self.logger.warning("No programs found in config file")
            return

        for program_name, params in programs.items():
            self._validate_required_params(program_name, params)
            self._validate_and_transform_params(program_name, params)

    def _validate_required_params(self, program_name, params):
        for required_param in REQUIRED_PARAMS:
            if required_param not in params:
                self.logger.error("Program `{}` must contain `{}` param".format(program_name, required_param))
                raise ParseError("Program `{}` must contain `{}` param".format(program_name, required_param))

    def _validate_and_transform_params(self, program_name, params):
        for param_key, param_value in params.items():
            self._validate_param_exist(program_name, param_key)
            self._validate_param_type(program_name, param_key, param_value)
            self._apply_param_transformation(program_name, param_key, param_value)


    def _validate_param_exist(self, program_name, param_key):
        if param_key not in PARAMS_CONSTANTS:
            self.logger.warning("Program `{}` contains unknown param `{}`".format(program_name, param_key))

    def _validate_param_type(self, program_name, param_key, param_value):
        expected_type = _to_list(PARAMS_CONSTANTS[param_key]['expected_type'])

        if not isinstance(param_value, tuple(expected_type)):
            actual_type = type(param_value)
            self.logger.error("Program `{}` param `{}` must be `{}`, not `{}`".format(program_name, param_key, expected_type, actual_type))
            raise ParseError("Program `{}` param `{}` must be `{}`, not `{}`".format(program_name, param_key, expected_type, actual_type))

    def _apply_param_transformation(self, program_name, param_key, param_value):
        params_mapping = PARAMS_CONSTANTS[param_key]
        handler = params_mapping.get('handler', _no_check)
        transform = params_mapping.get('transform')
        args = params_mapping.get('args', [])

        handler_return, handler_msg = handler(param_value, *args)
        if not handler_return:
            self.logger.error("Program `{}` param `{}` {}".format(program_name, param_key, handler_msg))
            raise ParseError("Program `{}` param `{}` {}".format(program_name, param_key, handler_msg))
        if transform:
            self.config['programs'][program_name][param_key] = transform(param_value, *args)

    @classmethod
    def from_command_line(cls):
        parser = argparse.ArgumentParser(description="Config file")
        parser.add_argument(
            '--config_path',
            '-c',
            required=True,
            type=str,
            help="Path to config file"
        )
        args = parser.parse_args()
        return cls(args.config_path)

if __name__ == '__main__':
    daemon_parser = DaemonParser().from_command_line()