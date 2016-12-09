BUFFER_SIZE = 1024
SHIELDING_BYTE = 0x25
STOP_BYTE = 0x26


def recv_until_end_from(sock):
    data = bytearray()
    finish_recieving = False

    while not finish_recieving:
        recieved_data = sock.recv(BUFFER_SIZE)

        if not recieved_data: break

        is_shielded = False
        for i in recieved_data:
            if not is_shielded and i == SHIELDING_BYTE:
                is_shielded = True
            elif not is_shielded and i == STOP_BYTE:
                finish_recieving = True
                break
            else:
                is_shielded = False
                data.append(i)
    return bytes(data)

def send_to(sock, data):
    prepared_data = bytearray()
    for i in data:
        if i == SHIELDING_BYTE or i == STOP_BYTE:
            prepared_data.append(SHIELDING_BYTE)
        prepared_data.append(i)
    prepared_data.append(STOP_BYTE)
    sock.send(prepared_data)