import logging
import threading
from asyncore import loop

import yaml

import commandhandler as CommandHandler
import warnings

from ConfigManager import ConfigManager

warnings.filterwarnings("ignore", category=DeprecationWarning, module="asyncore")

all_processes = {}

log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = logging.FileHandler('log_taskmaster.log', 'w', 'utf-8')
log.addHandler(handler)

def drop_privileges():
    import os
    import pwd
    import grp

    uid = pwd.getpwnam("nobody").pw_uid
    gid = grp.getgrnam("nogroup").gr_gid
    os.setgid(gid)
    os.setuid(uid)

    os.umask(0o77)

def main():

    # drop_privileges() # bonus

    configmanager = ConfigManager()
    commandeer = CommandHandler.CommandHandler()

    commandeer.all_processes = configmanager.create_processes(configmanager.config_data)

    for process_manager in commandeer.all_processes.values():
        process_manager.update_process_statuses()

    print(yaml.dump(commandeer.all_processes, default_flow_style=False))


    threads = threading.Thread(target=loop)
    threads.daemon = True
    threads.start()
    CommandHandler.CommandHandler.cmdloop(commandeer)

# TODO Добавить параллельную проверку статуса выполнения процесса (завершён, завершён с ошибкой ...). Если он завершён, то в статусе показать, что завершен.
if __name__ == "__main__":
    main()