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
        recv_task = asyncio.create_task(loop.sock_recvfrom(self.udp_sock, 1024))
        try:
            while True:
                try:
                    data, address = await recv_task
                    if data == settings.udp_request:
                        print(f'Обнаружен UDP-discovery запрос с адреса {address}, отвечаю...')
                        await loop.sock_sendto(self.udp_sock, settings.udp_response, address)
                        recv_task = asyncio.create_task(loop.sock_recvfrom(self.udp_sock, 1024))
                    elif data == settings.udp_kill:
                        print(f'Обнаружен UDP-запрос на прекращение работы с адреса {address}, начинаю завершение работы сервера...')
                        print("UDP сервер получает запрос на отмену...")
                        return
                    else:
                        recv_task = asyncio.create_task(loop.sock_recvfrom(self.udp_sock, 1024))
                        continue
                except Exception:
                    recv_task = asyncio.create_task(loop.sock_recvfrom(self.udp_sock, 1024))
                    continue
        except asyncio.CancelledError:
            raise
        except:
            print("Фатальное исключение на UDP сервере, завершается работа и пробрасывается исключение...")
            raise
        finally:
            recv_task.cancel()
            await asyncio.gather(recv_task, return_exceptions=True)
            self.udp_sock.close()
            print("UDP сервер завершил работу.")