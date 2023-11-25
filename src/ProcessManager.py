
class ProcessManager:

    def __init__(self, name, command):
        self.name = name
        self.command = command.get("command", None) # • The command to use to launch the program
        self.numprocs = command.get("numprocs", 1) # • The number of processes to start and keep running
        self.autostart = command.get("autostart", False) #  • Whether to start this program at launch or not
        self.autorestart = command.get("autorestart", False) # Whether the program should be restarted always, never, or on unexpected exits only
        self.returncodes = command.get("returncodes", [0]) # • Which return codes represent an "expected" exit status
        self.startsecs = command.get("startsecs", 1) # How long the program should be running after it’s started for it to be considered "successfully started"
        self.startretries = command.get("startretries", 3) # • How many times a restart should be attempted before aborting
        self.graceful_signal = command.get("graceful_signal", None) #  • Which signal should be used to stop (i.e. exit gracefully) the program
        self.graceful_timeout = command.get("graceful_timeout", None) # • How long to wait for the program to exit gracefully before sending the kill signal
        self.stdout_logfile = command.get("stdout_logfile", None) #• Options to discard the program’s stdout/stderr or to redirect them to files
        self.stderr_logfile = command.get("stderr_logfile", None) # • Options to discard the program’s stdout/stderr or to redirect them to files
        self.environment = command.get("environment", None) # • Environment variables to set before launching the program
        self.working_dir = command.get("working_dir", None) # • The working directory to use when the program is launched
        self.unmask = command.get("umask", None) # • An umask to set before launching the program