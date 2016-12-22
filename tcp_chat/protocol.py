import struct

LEN_STRUCT = struct.Struct('<I') # unsigned int

def recv_until_end_messages(sock):
    received_data_len = LEN_STRUCT.unpack(sock.recv(LEN_STRUCT.size))[0]
    received_data = b''

    while len(received_data) < received_data_len:
        received_data += sock.recv(received_data_len-len(received_data))

    return received_data


def send_message(sock, data):
    sock.send(LEN_STRUCT.pack(len(data)) + data)