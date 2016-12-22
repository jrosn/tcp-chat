import sys
import socket
import select

from .protocol import send_message, recv_until_end_messages
from .messages_pb2 import ChatRequest, ChatResponse

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
                    data = recv_until_end_messages(sock)

                    if data:
                        response = ChatResponse()
                        response.ParseFromString(data)

                        if response.HasField("message"):
                            print(response.message)
                        else:
                            print(response.client_ids)

                    else:
                        print("Disconnected from server")
                        sys.exit()
                else:
                    data = sys.stdin.readline()[:-1]

                    request = ChatRequest()
                    if data == "conn":
                        request.command_type = ChatRequest.GET_CLIENTS
                    else:
                        request.command_type = ChatRequest.BROADCAST_MSG
                        request.message = data

                    send_message(self.server_socket, request.SerializeToString())


    def start(self):
        self.server_socket.connect((self.host, self.port))
        try:
            self._input_loop()
        finally:
            self.server_socket.close()