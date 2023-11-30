import cmd

from termcolor import colored

from main import all_processes


class CommandHandler(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "taskmaster> "
        self.intro = "Welcome to Taskmaster, type ? to list commands"
        self.doc_header = "Taskmaster commands (type help <command>):"
        self.ruler = "-"
        self.config = None
        self.all_processes = {}

    def do_start(self, input_text):
        """Starts the processes"""
        process_name = input_text.split(" ")[0]
        if process_name in self.all_processes:
            self.all_processes[process_name].start()
        else:
            if process_name[0]:
                print(f"Process {process_name} not found")
            else:
                print("No process name given")

    def do_s(self, input_text):  # bonus alias for start
        self.do_start(input_text)

    def do_stop(self, input_text):
        """Stops the processes"""
        process_name = input_text.split(" ")[0]
        if process_name in self.all_processes:
            self.all_processes[process_name].stop()
        else:
            if process_name[0]:
                print(f"Process {process_name} not found")
            else:
                print("No process name given")

    def do_status(self, input_text):
        """Shows the status of the processes"""
        # Print headers
        header = "{:<20} {:<10} {:<20} {:<20} {:<20}".format(
            'PROGRAM', 'PID', 'PROCESSES RUNNING', 'START TIME', 'FINISH TIME'
        )
        print(colored(header, 'blue'))  # Header in blue color
        print(colored("-" * len(header), 'green'))  # Separator line in green color

        process_name = input_text.split(' ')[0]
        if process_name in self.all_processes:
            self.all_processes[process_name].check_status()
        elif not process_name:  # No specific process name was provided
            for process_name in self.all_processes:
                self.all_processes[process_name].check_status()
