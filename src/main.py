import logging
import threading
from asyncore import loop
import CommandHandler
from parse_configs import parse_config
from create_processes import create_processes
import warnings
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
    configurations = parse_config()
    create_processes(configurations)
    all_processes = create_processes(configurations)

    threads = threading.Thread(target=loop)
    threads.daemon = True
    threads.start()
    CommandHandler.CommandHandler().cmdloop()


   # drop_privileges() # bonus


if __name__ == "__main__":
    main()