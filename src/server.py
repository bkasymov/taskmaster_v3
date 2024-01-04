import json
import logging
import os
import signal
from threading import Lock

import logger

LOGLEVEL = getattr(logging, os.environ.get('LOGLEVEL', 'INFO'), logging.INFO)

class Server:
    def __init__(self, manager):
        self.manager = manager
        self.logger = logger.Logger(level=LOGLEVEL)
        self.lock = Lock()
        signal.Signals(signal.SIGINT, self._handle_keyboard_interrupt)

        def _handle_keyboard_interrupt(self, *_):
            self.logger.warning("CTRL+C pressed. Stopping server")
            self.manager.stop_all()
            raise KeyboardInterrupt

        def application(self, environ, start_response):
            with self.lock:
                request_body = self._read_request_body(environ)
                response_data = self._process_request(request_body)
                return self._create_response(start_response, response_data)

        def _read_request_body(self, environ):
            try:
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            except ValueError:
                request_body_size = 0
            return environ['wsgi.input'].read(request_body_size)

        def _process_request(self, request_body):
            data = json.loads(request_body)
            return self.manager.load_tcp_command(data)

        def _create_response(self, start_response, response_data):
            start_response('200 OK', [('Content-Type', 'application/json'),
                                      ('Access-Control-Allow-Origin', '*'),
                                      ('Access-Control-Allow-Headers', 'Content-Type'),
                                      ('Access-Control-Allow-Methods', 'GET, POST, PATCH, PUT, DELETE, OPTIONS'),
                                      ('Access-Control-Allow-Credentials', 'true')])
            return [json.dumps(response_data).encode()]

        def serve(self):
            serve(self.application, listen='*:8080')
