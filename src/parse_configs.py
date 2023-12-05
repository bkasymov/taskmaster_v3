class DaemonParser:
    def __init__(self, config_path):
        self.config_path = config_path
        self.logger = Logger(level=LOGLEVELCONSTANT)

    @classmethod
    def from_command_line(cls):
        parser = argparse.ArgumentParser(description="Config file")
        parser.add_argument(
            '--config_path',
            '-c', required=True,
            type=str,
            help="Path to config file"
        )
        args = parser.parse_args()
        return cls(args.config_path)

if __name__ == '__main__':
    daemon_parser = DaemonParser().from_command_line()