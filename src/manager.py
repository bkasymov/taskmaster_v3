import logging
import os

from logger import Logger

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

