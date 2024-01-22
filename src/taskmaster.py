import sys
import json
from urllib import request, parse

def sendRequest(data):
    req = request.Request("http://localhost:8080", data=data, headers={'content-type': 'application/json'})
    try:
        resp = request.urlopen(req)
        return json.loads(resp.read().decode())
    except Exception as e:
        return f"Ошибка: {e}"

def getStatus():
    data = json.dumps({"command": "refresh"}).encode('utf-8')
    return sendRequest(data)

def processCommand(command, args):
    globalStatus = getStatus()
    if isinstance(globalStatus, str):
        print(globalStatus)
        return
    availableTaskNames = [task_data["task"] for task_data in globalStatus]
    for argName in args:
        if argName not in availableTaskNames:
            print(argName, 'ERROR (no such process)')
            return
    data = json.dumps({"command": command, "args": args}).encode('utf-8')
    response = sendRequest(data)
    if isinstance(response, list):
        for item in response:
            print(item['task'], item['message'])
    elif isinstance(response, dict):
        print(response.get('task', ''), response.get('message', ''))

def printHelp(command=None):
    helpMessages = {
        "exit": 'exit    Exit the supervisor shell.',
        "start": 'start <name> Start a process\nstart <name> <name> Start multiple processes or groups\nstart all Start all processes',
        # Добавьте остальные команды и их описания здесь
    }
    print(helpMessages.get(command, 'default commands (type help <topic>):\n=====================================\n' + '\n'.join(helpMessages.keys())))

# TODO сервер запускается. Не работают команды. Поэтому нужно продебажить.

while True:
    print('taskmaster> ', end="")
    line = input()
    tab = line.split()
    if not tab:
        continue

    command, args = tab[0], tab[1:]
    if command == 'exit':
        print('Found exit. Terminating the program')
        break
    elif command == 'help':
        printHelp(args[0] if args else None)
    elif command in ['start', 'stop', 'restart']:
        processCommand(command, args)
    # Добавьте обработку других команд здесь
    else:
        print('*** Unknown syntax:', command)
