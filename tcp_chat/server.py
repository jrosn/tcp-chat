# coding=utf-8

import collections
import socket
import select
import uuid
from logging import info as log_info

from .messages_pb2 import ChatRequest, ChatResponse
from .protocol import recv_until_end_messages, send_message


class Client(collections.namedtuple('Client', 'id sock addr')):
    def __str__(self):
        return "Client({})".format(self.id)


class ChatServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connected_clients = []
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _register_client(self, client):
        self.connected_clients.append(client)

    def _unregister_and_close_client(self, client):
        self.connected_clients.remove(client)
        client.sock.close()

    def _get_client_by_sock(self, sock):
        clients = list(filter(lambda x: x.sock == sock, self.connected_clients))
        assert len(clients) == 1
        return clients[0]

    def _send_message_to_client(self, client, message):
        response = ChatResponse()
        response.message = message
        send_message(client.sock, response.SerializeToString())

    def _send_broadcast_message(self, message):
        for client in self.connected_clients:
            self._send_message_to_client(client, message)

    def _input_loop(self):
        while True:
            socks_to_read = list(map(lambda x: x.sock, self.connected_clients))

            # Linux epoll magic
            socks_ready_to_read, _, _ = select.select([self.server_sock] + socks_to_read, [], [])

            for sock in socks_ready_to_read:
                if sock == self.server_sock:
                    sock, addr = self.server_sock.accept()
                    new_client = Client(id=uuid.uuid4(), sock=sock, addr=addr)
                    self._register_client(new_client)
                    self._send_message_to_client(new_client, "{}".format(new_client.id).encode())

                    log_info("{} connected".format(str(new_client)))
                else:
                    client = self._get_client_by_sock(sock)
                    data = recv_until_end_messages(client.sock)
                    if not data:
                        self._unregister_and_close_client(client)
                        log_info("{} is offline (initiated by the client)".format(str(client)))
                        continue

                    log_info("recieved {len} bytes from {client}: {data}".format(
                        len=len(data),
                        client=client,
                        data=data
                    ))

                    request = ChatRequest()
                    request.ParseFromString(data)
                    if request.command_type == ChatRequest.BROADCAST_MSG:
                        self._send_broadcast_message(request.message)
                    elif request.command_type == ChatRequest.GET_CLIENTS:
                        client_ids = list(map(lambda x: x.id, self.connected_clients))
                        self._send_broadcast_message(str(client_ids).encode())

    def start(self):
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(10)
        try:
            self._input_loop()
        finally:
            self.server_sock.shutdown(0)
            self.server_sock.close()
