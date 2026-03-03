import asyncio, socket

import settings


class UdpDiscoverer:
    """
    UDP-сервер для принятия broadcast-запросов и ответов на них. Запуск через корутину work, завершение через отмену work и вызов функции close.
    """
    def __init__(self):
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.setblocking(False)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_sock.bind(settings.server_addr)
    
    
    async def work(self):
        loop = asyncio.get_running_loop()
        while True:
            try:
                data, address = await loop.sock_recvfrom(self.udp_sock, 1024)
                if data == settings.udp_request:
                    print(f'Обнаружен UDP-discovery запрос с адреса {address}, отвечаю...')
                    await loop.sock_sendto(self.udp_sock, settings.udp_response, address)
            except Exception:
                pass
    
    
    def close(self):
        self.udp_sock.close()