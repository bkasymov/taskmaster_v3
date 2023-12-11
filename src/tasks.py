import os
import signal
import subprocess
import time

from constants import LOGLEVELCONSTANT
from logger import Logger


def _nop():
    pass
class Task:
    def __init__(self, *args, **kwargs):
        self.logger = Logger(level=LOGLEVELCONSTANT)
        self.processes = []
        self.start_time = -1
        self.stdout = None
        self.stderr = None
        self.trynum = 1
        self.threads = []
        self.stopping = False

        self.update(*args, **kwargs)
        self.logger.debug("Task created")

    def update(self,
               name,
               cmd,
               numprocs=1,
               umask='665',
               workingdir=os.getcwd(),
               autostart=True,
               autorestart='unexpected',
               exitcodes=[0],
               startretries=1,
               starttime=5, # Задержка перед запуском
               stopsignal='TERM',
               stoptime=5, # Задержка перед остановкой
               env = {},
               **kwargs):
        self.name = name
        self.cmd = cmd
        self.numprocs = numprocs
        self.umask = umask
        self.workingdir = workingdir
        self.autostart = autostart
        self.autorestart = autorestart
        self.exitcodes = exitcodes
        self.startretries = startretries
        self.starttime = starttime
        self.stopsignal = stopsignal
        self.stoptime = stoptime
        self.env = os.environ

        for key, value in env.items():
            self.env[key] = str(value)

        self.stdout = kwargs.get('stdout', '')
        self.stderr = kwargs.get('stderr', '')

        if autostart:
            if self.is_running:
                self.restart()
            else:
                self.run()





    def run(self, retry=False):
        """
        :param retry:
        :return:
        """
        self.update_trynum(retry)
        if self.has_exceeded_retries():
            return

        self.reopen_stds()
        self.log_start_attempt()

        try:
            self.start_processes()
        except Exception:
            self.handle_startup_failure()

    def update_trynum(self, retry):
        self.trynum = 1 if not retry else (self.trynum + 1)

    def has_exceeded_retries(self):
        if self.trynum > self.startretries:
            self.logger.warning(f'{self.name} reached the maximum number of retries.')
            return True
        return False

    def log_start_attempt(self):
        self.logger.info(f'Try to start {self.name}. Retry attempt {self.trynum}, max retries: {self.startretries}, cmd: `{self.cmd}`')

    def start_processes(self):
        for virtual_pid in range(self.numprocs):
            process = self.start_process(virtual_pid)
            self.processes.append(process)
            self.start_time = time.time()

            if self.is_successful_start(process, virtual_pid):
                continue
            else:
                self.handle_unsuccessful_start(process, virtual_pid)

    def start_process(self, virtual_pid):
        return subprocess.Popen(
            self.cmd.split(),
            stderr=self.stderr,
            stdout=self.stdout,
            env=self.env,
            cwd=self.workingdir,
            preexec_fn=self._initchildproc,
        )

    def is_successful_start(self, process, virtual_pid):
        if process.returncode in self.exitcodes:
            self.define_restart_policy(process)
            self.logger.success(f'{self.name}: process number {virtual_pid} started. Exited directly, with returncode {process.returncode}')
            self.start_time = -2
            self.trynum = 1
            return True
        return False

    def handle_unsuccessful_start(self, process, virtual_pid):
        try:
            process.wait(timeout=self.starttime)

            if self.is_successful_start(process, virtual_pid):
                return
        except subprocess.TimeoutExpired:
            self.define_restart_policy(process)
            self.logger.success(f'{self.name}: process number {virtual_pid} started.')
            self.trynum = 1
            return
        self.logger.info(f'Unexpected returncode {process.returncode}')
        self.restart(retry=True)

    def handle_startup_failure(self):
        self.logger.warning(f'{self.name} startup failed.')
        self.restart(retry=True)






    @property
    def is_running(self):
            return self.start_time > 0


    def restart(self, retry=False, from_thread=False):
        """
        Если метод вызывается из потока, то проверяется, не находится ли процесс в состоянии остановки.
        Если да, то метод завершается.
        :param retry:
        :param from_thread:
        :return:
        """
        if from_thread and self.stopping:
            return

        self.stop(from_thread)
        self.run(retry=retry)

    def reopen_stds(self):
        if getattr(self.stdout, 'closed', True):
            self.stdout = getattr(self.stdout, 'name', '')
        if getattr(self.stderr, 'closed', True):
            self.stderr = getattr(self.stderr, 'name', '')






    def stop(self, from_thread=False):
        self.stopping = True
        self.close_fds()
        self._stop_processes()
        if not from_thread:
            self._stop_threads()
        self.processes = list()
        self.threads = list()
        self.start_time = -3 # Для того, чтобы при следующей проверке is_running процесс запускался заново
        self.stopping = False
    def _stop_processes(self):
        """Останавливает все процессы, связанные с задачей."""
        for process in self.processes:
            self.log.info(f'Send SIG{self.stopsignal} to {process.pid}.')
            process.send_signal(getattr(signal, 'SIG' + self.stopsignal))

            try:
                process.wait(self.stoptime)
            except subprocess.TimeoutExpired:
                self.log.info(f'Force kill {process.pid}.')
                process.kill()
    def _stop_threads(self):
        """Waits for the completion of all threads, handling potential issues."""
        for thread in self.threads:
            thread.join(1)  # Increasing the wait time to 1 second

            if thread.is_alive():
                # Logging if the thread is still active after the waiting period
                self.log.warning(f'Thread {thread.name} did not finish in time.')



# TODO ещё не все методы от файла task добавил. https://improved-dollop-4wx96vp4xpv2qrq6.github.dev/

    def close_fds(self):
        getattr(self.stdout, 'close', _nop)()
        getattr(self.stderr, 'close', _nop)()


