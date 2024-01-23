import os
import signal
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from constants import LOGLEVELCONSTANT, STATUS
from logger import Logger

def handle_process_restart_behavior(process,
                                    autorestart,
                                    exitcodes,
                                    restart_callback):
    
    process.wait()

    logger = Logger(level=LOGLEVELCONSTANT)
    logger.debug(f'Process {process.pid} ({process.args}) exited with returncode {process.returncode}.'
                 f'Expected exitcodes: {exitcodes}'
                 f'Autorestart: {autorestart}')

    if autorestart.upper() == 'ALWAYS' or (autorestart.upper() == 'UNEXPECTED' and
                                           process.returncode not in exitcodes and '*' not in process.returncode):
        try:
            logger.debug(f'Process {process.pid} ({process.args}) will be restarted by callback %s.' % restart_callback.__name__)
            restart_callback(process)
            return
        except Exception as e:
            logger.error(f'Error in callback: {e} {restart_callback.__name__} with args {process}')

def _nop():
    pass
class Task:
    def __init__(self, *args, **kwargs):
        self.logger = Logger(level=LOGLEVELCONSTANT)

        self.processes = list()
        self.start_time = STATUS['NOT_STARTED']
        self.stdout = ''
        self.stderr = ''
        self.trynum = 1
        self.threads = list()
        self.stopping = False

        self.update(*args, **kwargs)
        self.logger.debug("Task has created")

    def update(self,
               name,
               cmd,
               numprocs=1,
               umask='666',
               workingdir=os.getcwd(),
               autostart=False,
               autorestart='unexpected',
               exitcodes=[0],
               startretries=2,
               starttime=5, # Задержка перед запуском
               stopsignal='TERM',
               stoptime=10, # Задержка перед остановкой
               env={},
               **kwargs):


        self.env = os.environ
        self.exitcodes = exitcodes
        self.name = name
        self.cmd = cmd
        self.numprocs = numprocs
        self.umask = str(umask) if isinstance(umask, int) else '666'
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


    def close_fds(self):
        getattr(self.stdout, 'close', _nop)()
        getattr(self.stderr, 'close', _nop)()


    def reopen_stds(self):
        if getattr(self.stdout, 'closed', True):
            self.stdout = getattr(self.stdout, 'name', '')
        if getattr(self.stderr, 'closed', True):
            self.stderr = getattr(self.stderr, 'name', '')

    @property
    def stdout(self):
        return self._stdout

    @stdout.setter
    def stdout(self, path):
        if not path:
            self._stdout = subprocess.PIPE
            return
        else:
            self._stdout = open(path, 'a')

    @property
    def stderr(self):
        return self._stderr

    @stderr.setter
    def stderr(self, path):
        if not path:
            self._stderr = subprocess.PIPE
            return
        else:
            self._stderr = open(path, 'w')


    def _initchildproc(self):
        """
        Метод, который вызывается перед запуском дочернего процесса для того, чтобы изменить права доступа производных файлов и директорий.
        Аргумент 8 означает, что права доступа будут установлены в 8-ричной системе счисления.
        :return:
        """
        os.umask(int(self.umask, 8))

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

    def define_restart_policy(self, process, retry=False):
        thr = threading.Thread(
            target=handle_process_restart_behavior,
            args=(
                process,
                self.autorestart,
                self.exitcodes,
                lambda *_:
                    self.restart(retry=retry, from_thread=True),
            ),
            daemon=True,
        )
        thr.start()
        self.threads.append(thr)


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
        self.start_processes()


    def update_trynum(self, retry):
        if not retry:
            self.trynum = 1
        else:
            self.trynum += 1

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
        try:
            result = subprocess.Popen(
            self.cmd.split(),
            stderr=self.stderr,
            stdout=self.stdout,
            env=self.env,
            cwd=self.workingdir,
            preexec_fn=self._initchildproc,
        )
            return result
        except Exception as e:
            self.logger.error(f'Error in {self.name} subprocess.Popen: {e}')
            self.restart(retry=True)


    def is_successful_start(self, process, virtual_pid):
        if process.returncode in self.exitcodes:
            self.define_restart_policy(process)
            self.logger.success(f'{self.name}: process number #{virtual_pid} started. Exited directly, with returncode {process.returncode}')
            self.start_time = STATUS['FINISHED']
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
            self.logger.success(f'{self.name}: process number {virtual_pid} has started.')
            self.trynum = 1
            return
        self.logger.info(f'Unexpected return code {process.returncode}')
        self.restart(retry=True)

    def handle_startup_failure(self):
        self.logger.warning(f'{self.name} startup failed.')
        self.restart(retry=True)






    @property
    def is_running(self):
            return self.start_time > 0











    def _handle_restart(self, process, retry):
        try:
            handle_process_restart_behavior(
                process,
                self.autorestart,
                self.exitcodes,
                lambda *_:
                    self.restart(retry=retry, from_thread=True),
            )
        except Exception as e:
            self.logger.error(f'Error in thread: {e}')



    def stop(self, from_thread=False):
        self.stopping = True
        self.close_fds()
        self._stop_processes()
        if not from_thread:
            self._stop_threads()
        self.processes = list()
        self.threads = list()
        self.start_time = STATUS['STOPPED'] # Для того, чтобы при следующей проверке is_running процесс запускался заново
        self.stopping = False

    def _stop_processes(self):
        """Останавливает все процессы, связанные с задачей."""
        for process in self.processes:
            self.logger.info(f'Send SIG{self.stopsignal} to {process.pid}.')
            process.send_signal(getattr(signal, 'SIG' + self.stopsignal))

            try:
                process.wait(self.stoptime)
            except subprocess.TimeoutExpired:
                self.logger.info(f'Force kill {process.pid}.')
                process.kill()

    def _stop_threads(self):
        """Waits for the completion of all threads, handling potential issues."""
        for thread in self.threads:
            thread.join(1)  # Increasing the wait time to 1 second

            if thread.is_alive():
                # Logging if the thread is still active after the waiting period
                self.logger.warning(f'Thread {thread.name} did not finish in time.')
                thread.cancel()
                thread.join()





# TODO ещё не все методы от файла task добавил. https://improved-dollop-4wx96vp4xpv2qrq6.github.dev/




    def update_process_status(self):
        for process in self.processes:
            if process.returncode is not None:
                if process.returncode in self.exitcodes:
                    self.start_time = STATUS['FINISHED']
                else:
                    self.start_time = STATUS['STOPPED']
                return
        if not self.processes or all(process.returncode is None for process in self.processes):
            self.start_time = STATUS['NOT_STARTED']


    def uptime(self):
        self.update_process_status()
        if self.start_time == STATUS['NOT_STARTED']:
            return 'Not started'
        elif self.start_time == STATUS['STOPPED']:
            return 'Stopped'
        elif self.start_time == STATUS['FINISHED']:
            return 'Finished'

        uptime = int(time.time() - self.start_time)
        hours, remainder = divmod(uptime, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f'{hours}:{minutes}:{seconds}'


    def send_command(self, command):
        self.logger.info(f'Send command {command} to {self.name}')
        if command.upper() == 'RESTART':
            self.restart()
        elif command == 'stop':
            self.stop()
        elif command == 'start':
            self.run()
        else:
            return 'Unknown command'
        return 'Command sent'
    
    def get_uptime(self):
        return self.uptime()