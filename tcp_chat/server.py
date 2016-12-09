# coding=utf-8

import collections
import socket
import select
from logging import info as log_info
from .protocol import recv_until_end_from, send_to


class Client(collections.namedtuple('Client', 'sock addr')):
    def __str__(self):
        return "Client({})".format(self.addr)


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
        send_to(client.sock, message)

    def _send_broadcast_message(self, message):
        for client in self.connected_clients:
            self._send_message_to_client(client, message)

    def _message_handler(self, client, message):
        # <BAD CODE>
        for i in range(str(message).count("conn")):
            send_to(client.sock, str(self.connected_clients).encode())

        message_without_commands = message.decode().replace('conn', '').encode()
        if message_without_commands:
            self._send_broadcast_message(message_without_commands)
        # </BAD CODE>

    def _input_loop(self):
        while True:
            socks_to_read = list(map(lambda x: x.sock, self.connected_clients))

            # Linux epoll magic
            socks_ready_to_read, _, _ = select.select([self.server_sock] + socks_to_read, [], [])

            for sock in socks_ready_to_read:
                if sock == self.server_sock:
                    sock, addr = self.server_sock.accept()
                    new_client = Client(sock=sock, addr=addr)
                    self._register_client(new_client)

                    log_info("{} connected".format(str(new_client)))
                else:
                    client = self._get_client_by_sock(sock)
                    data = recv_until_end_from(client.sock)
                    if not data:
                        self._unregister_and_close_client(client)
                        log_info("{} is offline (initiated by the client)".format(str(client)))
                        continue

                    log_info("recieved {len} bytes from {client}: {data}".format(
                        len=len(data),
                        client=client,
                        data=data
                    ))

                    self._message_handler(client, data)

    def start(self):
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(10)
        try:
            self._input_loop()
        finally:
            self.server_sock.close()
