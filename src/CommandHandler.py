import cmd

from main import all_processes
from main import all_processes
class CommandHandler(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "taskmaster> "
        self.intro = "Welcome to Taskmaster, type ? to list commands"
        self.doc_header = "Taskmaster commands (type help <command>):"
        self.ruler = "-"
        self.config = None
        self.all_processes = all_processes

    def do_start(self, input):
        """Starts the processes"""
        process_name = input.split(" ")[0]
        if process_name in self.all_processes:
            self.all_processes[process_name].start()
        else:
            if process_name[0]:
                print(f"Process {process_name} not found")
            else:
                print("No process name given")

    def do_s(self, input): # bonus alias for start
        self.do_start(input)

    def do_stop(self, input):
        """Stops the processes"""
        process_name = input.split(" ")[0]
        if process_name in self.all_processes:
            self.all_processes[process_name].stop()
        else:
            if process_name[0]:
                print(f"Process {process_name} not found")
            else:
                print("No process name given")

    def do_status(self, input):
        """Shows the status of the processes"""
        process_name = input.split(" ")[0]
        if process_name in self.all_processes:
            self.all_processes[process_name].status()
        else:
            for process in self.all_processes:
                self.all_processes[process].status()