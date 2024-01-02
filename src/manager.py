import copy
import logging
import os

from logger import Logger
from tasks import Task

LOGLEVEL = getattr(logging, os.environ.get('LOGLEVEL', 'INFO'), logging.INFO)

class Manager:
    programs = list()

    def __init__(self, programs, parser):
        self.programs = programs
        self.parser = parser
        self.logger = Logger(level=LOGLEVEL)

    def stop_all(self):
        for program in self.programs:
            program.stop()

            for thread in program.threads:
                thread.join(.1)

    def _get_program_by_name(self, name):
        for program in self.programs:
            if program.name == name:
                return program
        return None

    def _remove_program_by_name(self, name):
        for program in self.programs:
            if program.name == name:
                self.programs.remove(program)
                self.logger.info("Program {} removed".format(name))
                return True
        return False

    def update(self):
        self.logger.info("Updating programs")
        difference = self.parser.refresh()
        self.logger.info("Difference: {}".format(difference))

        self._update_existing_programs(difference)
        self._add_new_programs(difference)
        self._stop_and_remove_unaffected_programs(difference)

        return {"raw_output": "Updated tasks %s" % difference, "updated_tasks": difference}

    def _update_existing_programs(self, difference):
        programs_names = [program.name for program in self.programs]
        changed_programs = []

        for program_name, _program_params in self.parser.configuration.get('programs', {}).items():
            if program_name in programs_names:
                program_params = copy.deepcopy(_program_params)
                cmd = program_params.pop('cmd')

                if program_params not in difference:
                    continue

                changed_programs.append(program_name)
                program = self._get_program_by_name(program_name)
                program.update(program_name, cmd, **program_params)

    def _add_new_programs(self, diff):
        programs_names = [program.name for program in self.programs]

        for program_name, _program_params in self.parser.configuration.get('programs', {}).items():
            if program_name not in programs_names:
                program_params = copy.deepcopy(_program_params)
                cmd = program_params.pop('cmd')
                program = Task(program_name, cmd, **program_params)
                self.programs.append(program)

    def _stop_and_remove_unaffected_programs(self, diff):
        programs_names = [program.name for program in self.programs]
        affected = [program_name for program_name, _ in self.parser.configuration.get('programs', {}).items()]

        for program_name in programs_names:
            if program_name not in diff and program_name not in affected:
                program = self._get_program_by_name(program_name)
                program.stop()
                self._remove_program_by_name(program_name)

    # TODO next method for write is load_tcp_command
    # TODO check all methods with write at the main method daemon.py