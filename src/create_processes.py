from ProcessManager import ProcessManager
from parse_configs import all_processes


def create_processes(configurations):
    for process_name in configurations:
        process = ProcessManager(process_name, configurations[process_name])
        all_processes[process_name] = process
