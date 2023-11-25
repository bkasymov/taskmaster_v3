from parse_configs import parse_config
from create_processes import create_processes


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
    drop_privileges() # bonus



if __name__ == "__main__":
    main()