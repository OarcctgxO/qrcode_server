import socket
import settings


def kill_all_servers():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    udp_sock.sendto(settings.udp_kill, ('255.255.255.255', 8888))


if __name__ == '__main__':
    kill_all_servers()