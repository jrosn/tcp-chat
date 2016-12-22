import struct
LEN_STRUCT = struct.Struct('<I') # unsigned int


def recv_until_end_messages(sock):
    len_bytes = sock.recv(LEN_STRUCT.size)
    if len(len_bytes) < LEN_STRUCT.size:
        return b''

    received_data_len = LEN_STRUCT.unpack(len_bytes)[0]
    received_data = b''

    while len(received_data) < received_data_len:
        received_data += sock.recv(received_data_len-len(received_data))

    return received_data


def send_message(sock, data):
    sock.send(LEN_STRUCT.pack(len(data)) + data)