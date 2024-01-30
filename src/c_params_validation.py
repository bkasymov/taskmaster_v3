import re
import subprocess
import os

def _path_checker(path):
    dirpath = os.path.dirname(os.path.abspath(path))
    if os.path.exists(dirpath):
        return True, ''
    else:
        return False, f'Cannot find directory {dirpath} for path {path}'


def _command_checker(command):
    if re.search(r'[<>&|]', command):
        return False, "Command must not contain `<>&|`"
    command_parts = command.split()
    if not command_parts:
        return False, "Command must not be empty"
    cmd = command_parts[0]

    try:
        # Создание процесса с командой, без его выполнения
        process = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Завершение процесса
        process.kill()
        process.wait()
        return True, ''
    except FileNotFoundError:
        # Если команда не найдена
        return False, f'Command `{cmd}` not found'

def _int_checker(integer, min_val, max_val):
    if min_val <= integer <= max_val:
        return True, ''
    else:
        return False, f'Number must be between {min_val} and {max_val}'


def _umask_checker(umask):
    umask_str = umask

    if len(umask_str) != 3:
        return False, 'Umask must be a 3-digit number.'

    for digit in umask_str:
        if not digit.isdigit() or int(digit) > 7:
            return False, 'Umask is not valid. Each digit must be between 0 and 7.'
    return True, ''


def _str_checker(string, *allowed_strings):
    upper_string = string.upper()

    if allowed_strings:
        if upper_string in (s.upper() for s in allowed_strings):
            return True, ''
        else:
            return False, f'"{string}" not in {allowed_strings}'
    else:
        return True, ''


def _exitcodes_checker(exitcodes):
    # Проверка, является ли exitcodes списком или кортежем
    if isinstance(exitcodes, (list, tuple)):
        for item in exitcodes:
            if not isinstance(item, int) and item != '*':
                return False, f'Unexpected exitcode {item}'
    # Проверка для одиночного значения exitcodes
    elif not isinstance(exitcodes, int) and exitcodes != '*':
        return False, f'Unexpected exitcode {exitcodes}'

    # Если все проверки пройдены успешно
    return True, ''

def _to_list(item):
    # Проверка, является ли item списком или кортежем
    if isinstance(item, (list, tuple)):
        return item
    # В противном случае, преобразование item в список
    return [item]


def _no_check(*args):
    return True, ''

def _create_path_if_not_exitsts(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w'):
        pass
    return path

PARAMS_CONSTANTS = {
    "cmd": {"expected_type": str, "handler": _command_checker},
    "numprocs": {"expected_type": int, "handler": _int_checker, "args": (1, 20)},
    "umask": {"expected_type": str, "handler": _umask_checker},
    "workingdir": {"expected_type": str, "handler": _path_checker},
    "autostart": {"expected_type": bool},
    "autorestart": {"expected_type": str, "handler": _str_checker, "args": ('ALWAYS', 'NEVER', 'UNEXPECTED')},
    "exitcodes": {"expected_type": (int, list, tuple, str), "handler": _exitcodes_checker, "transform": _to_list},
    "startretries": {"expected_type": int, "handler": _int_checker, "args": (1, 100)},
    "starttime": {"expected_type": int, "handler": _int_checker, "args": (0, 3600)},
    "stopsignal": {"expected_type": str, "handler": _str_checker, "args": (
        'HUP', 'INT', 'QUIT', 'ILL', 'TRAP', 'ABRT', 'EMT', 'FPE', 'KILL',
        'BUS', 'SEGV', 'SYS', 'PIPE', 'ALRM', 'TERM', 'USR1', 'USR2', 'CHLD',
        'PWR', 'WINCH', 'URG', 'POLL', 'STOP', 'TSTP', 'CONT', 'TTIN', 'TTOU',
        'VTALRM', 'PROF', 'XCPU', 'XFSZ', 'WAITING', 'LWP', 'AIO'
    )},
    "stoptime": {"expected_type": int, "handler": _int_checker, "args": (0, 20)},
    "stdout": {"expected_type": str, "handler": _path_checker, "transform": _create_path_if_not_exitsts},
    "stderr": {"expected_type": str, "handler": _path_checker, "transform": _create_path_if_not_exitsts},
    "env": {"expected_type": dict},
}

