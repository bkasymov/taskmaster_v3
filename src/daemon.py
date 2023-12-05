
LOGLEVELCONSTANT = getattr(logging, os.environ.get('LOGLEVEL', 'INFO'), logging.INFO)


class TaskmasterDaemon:
    def __init__(self, config_file):
        self.logger = Logger(level=LOGLEVELCONSTANT)
        self.parser = None
        self.programs = []
        self.manager = None
        self.server = None

    def parse_configs(self):
        try:
            self.logger.info("Parsing config file")
            self.parser = DaemonParser().from_command_line()
            self.logger.info("Config file parsed")
        except ConfigParserError as e:
            self.logger.error("Error parsing config file: {}".format(e))
            exit(-1)

    def create_tasks(self):
        for program in self.parser.programs:
            params = copy.deepcode(program_params)
            cmd = params.pop('cmd')
            task = Task(program.name, cmd, **params)
            self.programs.append(task)
        self.logger.info("Programs parsed")

    def setup_signal_handlers(self):
        def update_tcp_command(*_):
            self.manager.load_tcp_command({"command": "update"})
        signal.signal(signal.SIGHUB, update_tcp_command)

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

    taskmaster_daemon.start_server()

    taskmaster_daemon.stop_all()



