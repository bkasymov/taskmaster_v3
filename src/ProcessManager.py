import datetime
import logging
import os
import subprocess
import time

from termcolor import colored


class ProcessManager:

    def __init__(self, name, command):
        self.name = name
        self.command = command.get("command", None) # • The command to use to launch the program
        self.numprocs = command.get("numprocs", 1) # • The number of processes to start and keep running
        self.autostart = command.get("autostart", False) #  • Whether to start this program at launch or not
        self.autorestart = command.get("autorestart", False) # Whether the program should be restarted always, never, or on unexpected exits only #TODO в процессе
        self.returncodes = command.get("returncodes", [0]) # • Which return codes represent an "expected" exit status
        self.startsecs = command.get("startsecs", 1) # How long the program should be running after it’s started for it to be considered "successfully started"
        self.startretries = command.get("startretries", 3) # • How many times a restart should be attempted before aborting
        self.restart_count = 0
        self.graceful_signal = command.get("graceful_signal", None) #  • Which signal should be used to stop (i.e. exit gracefully) the program
        self.graceful_timeout = command.get("graceful_timeout", None) # • How long to wait for the program to exit gracefully before sending the kill signal
        self.stdout = command.get("stdout", None) #• Options to discard the program’s stdout/stderr or to redirect them to files
        self.stderr = command.get("stderr", None) # • Options to discard the program’s stdout/stderr or to redirect them to files
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

    import datetime

# FIXME Пересмотреть как убивать процессы
    # FIXME исправить, чтобы корректно записывалось время отключения процесса для показания на do_status
    def _kill_processes(self):
        for process in self.processes:
            process.kill()
            current_time = datetime.datetime.now()
            time_elapsed = current_time - self.start_time
            hours, remainder = divmod(time_elapsed.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            formatted_time = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
            logging.info(f"Killed {self.name} with pid {process.pid} and worked {formatted_time}")
            print(f"Killed {self.name} with pid {process.pid} and worked {formatted_time}")


    def _close_io_files(self):
        if self.stdout:
            self.stdout.close()
        if self.stderr:
            self.stderr.close()





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
        self.stdout = open(self.stdout, "w+") if self.stdout else None
        self.stderr = open(self.stderr, "w+") if self.stderr else None

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
                    stdout=self.stdout,
                    stderr=self.stderr,
                    env=self.environment
                )
                self.processes.append(process)
                self.start_time = datetime.datetime.now()
                formatted_time = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
                logging.info(f"Started {self.name} with pid {process.pid} at {formatted_time}")
                print(f"Started {self.name} with pid {process.pid} at {formatted_time}")
            except Exception as e:
                formatted_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"Error starting {self.name}: {e} at {formatted_time}")
                logging.error(f"Error starting {self.name}: {e} at {formatted_time}")


    def status(self):
        header = "{:<20} {:<10} {:<20} {:<20} {:<20}".format(
            'Program', 'PID', 'Processes Running', 'Start Time', 'Finish Time'
        )
        print(colored(header, 'blue'))  # Заголовок в синем цвете
        print(colored("-" * len(header), 'green'))  # Разделительная линия в зеленом цвете

        if self.processes:
            program_status = "{:<20} {:<10} {:<20} {:<20} {:<20}".format(
                self.name,
                self.processes[0].pid,
                len(self.processes),
                self.start_time.strftime("%Y-%m-%d %H:%M:%S") if self.start_time else 'N/A',
                self.finish_time.strftime("%Y-%m-%d %H:%M:%S") if self.finish_time else 'N/A'
            )
            print(colored(program_status, 'yellow'))  # Статус программы в желтом цвете
        else:
            program_status = "{:<20} {:<10} {:<20} {:<20} {:<20}".format(
                self.name,
                'N/A',
                '0',
                'N/A',
                'N/A'
            )
            print(colored(program_status, 'red'))  # Статус для неактивных программ в красном цвете

