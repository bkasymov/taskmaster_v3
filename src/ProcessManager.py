import logging
import os
import subprocess
import time


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
        self.restart_count = 0
        self.graceful_signal = command.get("graceful_signal", None) #  • Which signal should be used to stop (i.e. exit gracefully) the program
        self.graceful_timeout = command.get("graceful_timeout", None) # • How long to wait for the program to exit gracefully before sending the kill signal
        self.stdout_logfile = command.get("stdout_logfile", None) #• Options to discard the program’s stdout/stderr or to redirect them to files
        self.stderr_logfile = command.get("stderr_logfile", None) # • Options to discard the program’s stdout/stderr or to redirect them to files
        self.environment = command.get("environment", None) # • Environment variables to set before launching the program
        self.working_dir = command.get("working_dir", None) # • The working directory to use when the program is launched
        self.umask = command.get("umask", None) # • An umask to set before launching the program
        self.old_umask = None
        self.processes = [] # • A list of the processes that are currently running
        self.start_time = None # • The time when the program was started
        self.finish_time = None # • The time when the program exited

        if self.autostart:
            self.start()


    def stop(self):
        self._print_stop_message()
        self._kill_processes()
        self._close_io_files()

    def _print_stop_message(self):
        print(f"Stopping {self.name}...")
        logging.info(f"Stopping {self.name}...")

    def _kill_processes(self):
        for process in self.processes:
            process.kill()
            logging.info(f"Killed {self.name} with pid {process.pid} and worked {time.time() - self.start_time}")

    def _close_io_files(self):
        if self.stdout_logfile:
            self.stdout_logfile.close()
        if self.stderr_logfile:
            self.stderr_logfile.close()

    def start(self):
        self._print_start_message()
        self._set_umask()
        self._open_io_files()
        self._reset_umask()
        self._create_processes()


    def _print_start_message(self):
        print(f"Starting {self.name}...")
        logging.info(f"Starting {self.name}...")

    def _set_umask(self):
        self.old_umask = os.umask(0o22)

    def _open_io_files(self):
        self.stdout_logfile = open(self.stdout_logfile, "w+") if self.stdout_logfile else None
        self.stderr_logfile = open(self.stderr_logfile, "w+") if self.stderr_logfile else None

    def _reset_umask(self):
        os.umask(self.old_umask)

    def _create_processes(self):
        while len(self.processes) < self.numprocs:
            try:
                process = subprocess.Popen(
                    self.command,
                    cwd=self.working_dir,
                    shell=True,
                    stdin=subprocess.PIPE,
                    stdout=self.stdout_logfile,
                    stderr=self.stderr_logfile,
                    env=self.environment
                )
                self.processes.append(process)
                self.start_time = time.time()
                logging.info(f"Started {self.name} with pid {process.pid} at {self.start_time}")
                print(f"Started {self.name} with pid {process.pid} at {self.start_time}")
            except Exception as e:
                print(f"Error starting {self.name}: {e} at {self.start_time}")
                logging.error(f"Error starting {self.name}: {e} at {self.start_time}")



