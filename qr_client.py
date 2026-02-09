import socket
import base64
import select


try:
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    for i in range(5):
        udp_sock.sendto(b"Who's QRcode server?", ('255.255.255.255', 8888))
        r, _, _ = select.select([udp_sock], [], [], 1)
        if r:
            data, addr = udp_sock.recvfrom(1024)
            if data == b"I am the QRcode server.":
                break
        else:
            if i == 4:
                raise ConnectionError('Сервер не найден в локальной сети.' + 
                                    'Возможно, он не запущен или запущен в другой Wi-Fi сети')
    udp_sock.close()
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.connect(addr)
    text_to_code = 'sample text'
    tcp_sock.send(text_to_code.encode())
    data = tcp_sock.recv(102400)
    base64pictures = data.decode('ascii').split('|')
    base64pictures = [byte_string.encode('ascii') for byte_string in base64pictures if byte_string] #purge empty bytes
    counter = 1
    for b64pic in base64pictures:
        img_bytes = base64.b64decode(b64pic)
        with open(f'picture{counter}.png', 'wb') as file:
            file.write(img_bytes)
        counter += 1
except BaseException as er:
    print(er)
    input()