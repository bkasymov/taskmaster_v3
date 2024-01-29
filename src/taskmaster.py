import pprint
import sys
import json
from turtle import pd
from urllib import request

import constants

SERVER_PORT = constants.SERVER_PORT
HEADERS = {'content-type': 'application/json'}

class TaskMaster:
    def __init__(self):
        self.commands = {
            'start': self.start,
            'restart': self.restart,
            'stop': self.stop,
            'update': self.update,
            'status': self.status,
            'help': self.help,
            'exit': self.exit,
        }

    def send_request(self, command, args=None):
        """Send a request to the server with the given command and arguments."""
        data = json.dumps({"command": command, "args": args}).encode('utf-8')
        req = request.Request(f"http://localhost:{SERVER_PORT}", data=data, headers=HEADERS)
        try:
            resp = request.urlopen(req)
            return json.loads(resp.read().decode())
        except:
            print(f"Error: http://localhost:{SERVER_PORT} refused connection")
            return None

    def start(self, args):
        """Start one or more tasks."""
        if not args:
            print("Error: no tasks specified")
            return
        status = self.send_request("start", args)
        if status:
            self.print_status(status)

    def restart(self, args):
        """Restart one or more tasks."""
        status = self.send_request("restart", args)
        if status:
            self.print_status(status)

    def stop(self, args):
        """Stop one or more tasks."""
        status = self.send_request("stop", args)
        if status:
            self.print_status(status)

    def update(self, args):
        """Update the task configuration."""
        status = self.send_request("update")
        if status:
            print(status["raw_output"])

    def status(self, args):
        """Print the status of one or more tasks."""
        status = self.send_request("refresh")
        if status:
            for item in status:
                if not args or item["task"] in args:
                    print(
                        f"Task: {item['task']} | Pids: {item['pids']} | Started Processes: {item['started_processes']} | Uptime: {item['uptime']}")
    def help(self, args):
        """Print help information."""
        # Add your help messages here
        print("Help information...")

    def exit(self, args):
        """Exit the program."""
        sys.exit(0)

    def print_status(self, status):
        """Print the status returned from a command."""
        if isinstance(status, list):
            for item in status:
                print(f"Task: {item['task']} | Message: {item['message']} | Raw Output: {item.get('raw_output', '')}")
        elif isinstance(status, dict) and "error" not in status:
            print(f"Task: {status['task']} | Message: {status['message']} | Raw Output: {status.get('raw_output', '')}")


    def run(self):
        """Run the main loop, reading commands and executing them."""
        while True:
            print('taskmaster> ', end="")
            line = input().strip()
            if not line:
                continue
            parts = line.split()
            command, args = parts[0], parts[1:]
            if command in self.commands:
                self.commands[command](args)
            else:
                print(f"*** Unknown command: {command}")

if __name__ == "__main__":
    TaskMaster().run()