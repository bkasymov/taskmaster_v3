import subprocess
import threading
import time
import logging
import os
import signal

class Process:
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.start_time = None
        self.status = "STOPPED"
        self.instances = []
        self.num_instances = config.get('num_instances', 1)
        self.autostart = config.get('autostart', False)
        self.restart_policy = config.get('restart_policy', 'never')  # always, never, unexpected
        self.expected_exitcodes = config.get('exitcodes', [0])
        self.successful_start_time = config.get('successful_start_time', 0)
        self.max_restarts = config.get('max_restarts', 3)
        self.restart_attempts = 0
        self.graceful_stop_timeout = config.get('graceful_stop_timeout', 10)  # Время ожидания в секундах
        self.start_times = {}  # Словарь для отслеживания времени запуска каждого экземпляра
        self.stop_signal = config.get('stop_signal', signal.SIGTERM)  # Инициализация stop_signal

        if self.autostart:
            self.start()

    def start(self):
        while len(self.instances) < self.num_instances:
            self.status = "RUNNING"
            process = subprocess.Popen(
                self.config['command'],
                cwd=self.config.get('working_dir'),
                shell=True,
                stdout=self._get_output_stream(self.config.get('stdout')),
                stderr=self._get_output_stream(self.config.get('stderr')),
                env=self.config.get('env', {})
            )
            self.instances.append(process)
            logging.info(f"Process {self.name} is starting.")
            self.start_times[process] = time.time()  # Запись времени запуска для каждого экземпляра

    def stop(self):
        for process in self.instances:
            try:
                process.send_signal(self.stop_signal)
            except Exception as e:
                logging.error(f"Error sending stop signal to {self.name}: {e}")

        self.instances.clear()
        self.status = "STOPPED"
        logging.info(f"Process {self.name} stopped.")

    def _force_stop(self):
        logging.info(f"Force stopping all instances of {self.name}.")

        for process in self.instances:
            if process.poll() is None:  # Если процесс все еще работает
                process.kill()
        self.instances.clear()
        logging.info(f"All instances of {self.name} forcefully stopped.")

    def restart(self):
        logging.info(f"Restarting {self.name}.")
        self.stop()
        time.sleep(self.graceful_stop_timeout + 1)  # Убедимся, что процесс остановлен перед перезапуском
        self.start()


    def _setup_environment(self):
        os.umask(self.config.get('umask', 0o22))

    def _get_output_stream(self, path):
        if path:
            os.makedirs(os.path.dirname(path), exist_ok=True)  # Создание каталогов, если они не существуют
            return open(path, "a+")  # Открытие файла в режиме добавления
        return None

    def check_status(self):
        running_instances = 0
        for process in list(self.instances):
            if process.poll() is None:
                running_instances += 1
            else:
                self.instances.remove(process)
                logging.info(f"Process {self.name} instance stopped.")

        self.status = "RUNNING" if running_instances > 0 else "STOPPED"
        logging.info(f"Process {self.name} status updated to {self.status}.")

    def handle_exit(self, exitcode):
        if self.restart_policy == 'always':
            self.start()
        elif self.restart_policy == 'unexpected' and exitcode not in self.expected_exitcodes:
            self.start()

        if self.should_restart(exitcode):
            if self.restart_attempts < self.max_restarts:
                self.restart_attempts += 1
                self.start()
            else:
                logging.info(f"Max restart attempts reached for {self.name}. Not restarting.")
        else:
            self.restart_attempts = 0

    def should_restart(self, exitcode):
        if self.restart_policy == 'always':
            return True
        elif self.restart_policy == 'unexpected' and exitcode not in self.expected_exitcodes:
            return True
        return False

    def update_config(self, new_config):
        self.config = new_config
        self.num_instances = new_config.get('num_instances', 1)
        self.autostart = new_config.get('autostart', False)
        self.restart_policy = new_config.get('restart_policy', 'never')
        self.expected_exitcodes = new_config.get('exitcodes', [0])
        self.successful_start_time = new_config.get('successful_start_time', 0)
        self.max_restarts = new_config.get('max_restarts', 3)
        self.stop_signal = new_config.get('stop_signal', signal.SIGTERM)
        self.graceful_stop_timeout = new_config.get('graceful_stop_timeout', 10)