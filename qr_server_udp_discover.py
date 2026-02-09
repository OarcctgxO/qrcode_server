import asyncio, socket

import settings


class UdpDiscoverer:
    def __init__(self):
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.setblocking(False)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_sock.bind(settings.server_addr)
        self.work_task: asyncio.Task
    
    
    async def work_inner(self):
        loop = asyncio.get_running_loop()
        while True:
            try:
                data, address = await loop.sock_recvfrom(self.udp_sock, 1024)
                if data == settings.udp_request:
                    print(f'Обнаружен UDP-discovery запрос с адреса {address}, отвечаю...')
                    await loop.sock_sendto(self.udp_sock, settings.udp_response, address)
            except asyncio.CancelledError:
                print("UDP сервер получает запрос на отмену...")
                break
            except Exception:
                pass
        print("UDP сервер завершил работу.")
    
    async def work(self):
        self.work_task = asyncio.create_task(self.work_inner())
        await self.work_task
    
    def close(self):
        if hasattr(self, 'work_task') and not self.work_task.done():
            self.work_task.cancel('Socket is closed.')
        self.udp_sock.close()