import copy
import signal
import sys
from logger import Logger
from e_manager import Manager
from b_parse_configs import DaemonParser
from exceptions import ConfigParserError
from f_server import Server

from d_program import Task
from aa_constants import LOGLEVELCONSTANT


class TaskmasterDaemon:
    def __init__(self):
        self.logger = Logger(level=LOGLEVELCONSTANT)
        self.parser = None
        self.programs = []
        self.manager = None
        self.server = None

    def parse_configs(self):
        try:
            self.logger.info("Parsing config file")
            # Сначала вызывается статический метод, а затем создаётся объект DaemonParser сразу же.
            # Возвращается объект класса DaemonParser
            self.parser = DaemonParser.from_command_line()
            self.logger.info("Config file parsed")
            self.logger.success('')
        except ConfigParserError as e:
            self.logger.error("Error parsing config file: {}".format(e))
            exit(-1)

    def create_tasks(self):
        for program_name, program_params in self.parser.config['programs'].items():
            params = copy.deepcopy(program_params)
            cmd = params.pop('cmd')
            task = Task(program_name, cmd, **params)
            self.programs.append(task)
        self.logger.info("Programs parsed")

    def setup_signal_handlers(self):
        def update_tcp_command(*_):
            self.manager.load_tcp_command({"command": "update"})
        signal.signal(signal.SIGHUP, update_tcp_command)

    def start_server(self):
        try:
            self.logger.info("Starting server on `localhost:8080`")
            self.server = Server(self.manager)
            self.server.serve()
        except OSError as e:
            if e.errno == 98:
                self.logger.error("Port is already in use")
            else:
                self.logger.error("Error starting server: {}".format(e))
        except KeyboardInterrupt:
            self.logger.warning("Keyboard interrupt")
            sys.exit(-1)

    def stop_all(self):
        self.manager.stop_all()

# TODO названия потом поменяю, сейчас это не критично. Потом рефакторингом быстро одной клавишей поменяю.

if __name__ == '__main__':

    taskmaster_daemon = TaskmasterDaemon()

    taskmaster_daemon.parse_configs()

    taskmaster_daemon.create_tasks()

    taskmaster_daemon.manager = Manager(taskmaster_daemon.programs, taskmaster_daemon.parser)

    taskmaster_daemon.setup_signal_handlers()
    
    taskmaster_daemon.server = Server(manager=taskmaster_daemon.manager)
    taskmaster_daemon.server.serve()
    
    taskmaster_daemon.stop_all()



