import sys
import socket
import select
from .protocol import send_to, recv_until_end_from


class ChatClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _input_loop(self):
        # refactor this
        while True:
            # Linux epoll magic
            inputs_ready_to_read, _, _ = select.select([self.server_socket, sys.stdin], [], [])

            for sock in inputs_ready_to_read:
                if sock == self.server_socket:
                    data = recv_until_end_from(sock)
                    if data:
                        print(data.decode())
                    else:
                        print("Disconnected from server")
                        sys.exit()
                else:
                    data = sys.stdin.readline()[:-1]
                    send_to(self.server_socket, data.encode())

    def start(self):
        self.server_socket.connect((self.host, self.port))
        try:
            self._input_loop()
        finally:
            self.server_socket.close()