import cmd
import time

from configs import load_config


class TaskmasterShell(cmd.Cmd):
    intro = 'Welcome to Taskmaster. Type help or ? to list commands.\n'
    prompt = '(taskmaster) '

    def __init__(self, processes):
        super().__init__()
        self.processes = processes

    def do_start(self, arg):
        """Start a process: start <name>"""
        process = self.processes.get(arg)
        if process:
            process.start()
            print(f"Process {arg} started.")
        else:
            print(f"Process {arg} not found.")

    def do_stop(self, arg):
        """Stop a process: stop <name>"""
        process = self.processes.get(arg)
        if process:
            process.stop()
            print(f"Process {arg} stopped.")
        else:
            print(f"Process {arg} not found.")

    def do_restart(self, arg):
        """Restart a process: restart <name>"""
        process = self.processes.get(arg)
        if process:
            process.restart()
            print(f"Process {arg} restarted.")
        else:
            print(f"Process {arg} not found.")

    def do_status(self, arg):
        """Check the status of processes: status [<name>]"""
        if arg:
            # Показать статус одного процесса
            self._show_process_status(arg)
        else:
            # Показать статус всех процессов
            for name in self.processes:
                self._show_process_status(name)


    def _show_process_status(self, name):
        process = self.processes.get(name)
        if process:
            uptime = self._get_process_uptime(process)
            print(f"{name:30} Status: {process.status:10}") # Uptime: {uptime:15}
        else:
            print(f"{name:20} Status: {'Not found':10}")# Uptime: {'N/A':15}

    def _get_process_uptime(self, process):
        if process.status == "RUNNING" and process.start_time:
            uptime = time.time() - process.start_time
            return time.strftime("%H:%M:%S", time.gmtime(uptime))
        return "Not running"

    def do_status(self, arg):
        if arg:
            self._show_process_status(arg)
        else:
            print(f"{'Process Name':30} {'Status':50}") # {'Uptime':15}
            print(f"{'-' * 20} {'-' * 10} {'-' * 15}")
            for name in self.processes:
                self._show_process_status(name)

    def do_reload(self, arg):
        """Reload the configuration file"""
        try:
            new_config = load_config('taskmaster_config.yml')
            # Обновление существующих и добавление новых процессов
            for name, config in new_config.items():
                if name in self.processes:
                    # Обновление конфигурации существующего процесса
                    self.processes[name].update_config(config)
                    if self.processes[name].autostart:
                        self.processes[name].restart()
                else:
                    # Добавление нового процесса
                    self.processes[name] = Process(name, config)
                    if config.get('autostart', False):
                        self.processes[name].start()
            # Удаление отсутствующих в новой конфигурации процессов
            for name in list(self.processes.keys()):
                if name not in new_config:
                    self.processes.pop(name).stop()
            print("Configuration reloaded.")
        except Exception as e:
            print(f"Error reloading configuration: {e}")



    def do_exit(self, arg):
        """Exit the taskmaster shell"""
        for process in self.processes.values():
            process.stop()
        print("Exiting Taskmaster...")
        return True  # Возвращает True для завершения цикла cmdloop

    def cmdloop(self, intro=None):
        print(self.intro)  # Печать приветственного сообщения
        while True:
            try:
                super(TaskmasterShell, self).cmdloop(intro="")
                break  # Выход из цикла после завершения cmdloop
            except KeyboardInterrupt:
                print("\nОперация прервана. Введите 'exit' для выхода.")

    def do_show(self, arg):
        """Show details of a process: show <name>"""
        process = self.processes.get(arg)
        if process:
            self._show_process_details(process)
        else:
            print(f"Process {arg} not found.")

    def _show_process_details(self, process):
        """Выводит подробные характеристики процесса."""
        print(f"Process Name: {process.name}")
        print(f"Status: {process.status}")
        if process.status == "RUNNING":
            uptime = self._get_process_uptime(process)
            print(f"Uptime: {uptime}")
        print("Configuration:")
        for key, value in process.config.items():
            print(f"  {key}: {value}")