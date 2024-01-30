import copy
import logging
import os

from aa_constants import LOGLEVELCONSTANT
from logger import Logger
from d_program import Task

class Manager:
    programs = list()

    def __init__(self, programs, parser):
        self.programs = programs
        self.parser = parser
        self.logger = Logger(level=LOGLEVELCONSTANT)

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
        if difference:
            self._update_existing_programs(difference)
            self._add_new_programs(difference)
            self._stop_and_remove_unaffected_programs(difference)

        return {"raw_output": "Updated tasks %s" % difference, "updated_tasks": difference}

    def _update_existing_programs(self, difference):
        programs_names = [program.name for program in self.programs]
        changed_programs = []

        for program_name, _program_params in self.parser.config.get('programs', {}).items():
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

        for program_name, _program_params in self.parser.config.get('programs', {}).items():
            if program_name not in programs_names:
                program_params = copy.deepcopy(_program_params)
                cmd = program_params.pop('cmd')
                program = Task(program_name, cmd, **program_params)
                self.programs.append(program)

    def _stop_and_remove_unaffected_programs(self, diff):
        programs_names = [program.name for program in self.programs]
        affected = [program_name for program_name, _ in self.parser.config.get('programs', {}).items()]
# FIXME should remove echo program, but he miss it.
        for program_name in programs_names:
            if program_name in diff and program_name not in affected:
                program = self._get_program_by_name(program_name)
                program.stop()
                self._remove_program_by_name(program_name)

    # TODO check all methods with write at the main method daemon.py

    def load_tcp_command(self, request):
        command = request.get('command', '').upper()
        args = request.get('args', [])
        with_refresh = request.get('with_refresh', False)

        if command == 'UPDATE':
            return self.handle_update(with_refresh)
        if command == "REFRESH":
            return self.handle_refresh(args)
        if command == "STOP_DAEMON":
            return self.handle_stop_daemon()
        return self.handle_command(command, args, with_refresh)

    def handle_update(self, with_refresh):
        response = self.update()
        if not with_refresh:
            return response
        return None

    def handle_refresh(self, args):
        if args:
            return self.get_programs_status(args)
        return self.get_programs_status()

    def handle_stop_daemon(self):
        self.stop_all()
        raise Exception("Stop daemon")

    def handle_command(self,
                       command,
                       args,
                       with_refresh):
        response = []


        if args[0] == 'all' and command == 'STOP':
            for program in self.programs:
                ret = self.execute_command_on_program(program, command)
                response.append(self.format_response(ret))
            return self.get_programs_status()

        for program in self.programs:
            if program.name in args:
                ret = self.execute_command_on_program(program, command)
                response.append(self.format_response(ret))
                args.remove(program.name)
        if not with_refresh:
            return response
        return self.get_programs_status()

    def execute_command_on_program(self, program, command):
        return program.send_command(command)

    def format_response(self, ret):
        if 'error' in ret:
            return {
                "raw_output": f"{ret['task']}: ERROR: {ret['message']}",
                **ret
            }
        else:
            return {
                "raw_output": f"{ret['task']}: {ret['message']}",
                **ret
            }

    def get_programs_status(self, args=None):
        if args is None:
            selected_programs = self.programs
        else:
            selected_programs = [program for program in self.programs if program.name in args]

        status_list = []
        for program in selected_programs:
            program_status = {
                "task": program.name,
                "uptime": program.get_uptime(),
                "started_processes": len(program.processes),
                "pids": [process.pid for process in program.processes],
            }
            status_list.append(program_status)
        return status_list