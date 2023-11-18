import yaml

from configs import setup_logging, reload_config, load_config
from parser import validate_config, initialize_processes
from process import Process
from taskmastershell import TaskmasterShell


def main():
    setup_logging()
    config_path = 'resources/general.test2'  # Путь к конфигурационному файлу
    config = load_config(config_path)
    if validate_config(config):
        print("Configuration loaded.")
    processes = initialize_processes(config)  # Инициализация процессов
    shell = TaskmasterShell(processes)

    # Добавление функции перезагрузки конфигурации в шелл
    shell.do_reload = lambda arg: reload_config(shell, config_path)
    shell.cmdloop()


if __name__ == '__main__':
    main()
