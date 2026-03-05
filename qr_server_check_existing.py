import socket as s
import asyncio

import settings


async def send_and_recv(udp_sock: s.socket):
    """
    Корутина, отправляющаяя broadcast запрос и ожидающаяя правильного ответа 1 секунду. Возвращает адрес ответившего. Если нет ответа - None.
    Нарочно не использует asyncio.timeout из-за проблем с отменой sock_recvfrom и выводом ошибок после прекращения работы программы
    """
    loop = asyncio.get_running_loop()
    await loop.sock_sendto(udp_sock, settings.udp_request, settings.broadcast_addr)
    get_task = asyncio.create_task(loop.sock_recvfrom(udp_sock, 1024))
    wait_task = asyncio.create_task(asyncio.sleep(1))
    while True:
        done, _ = await asyncio.wait([get_task, wait_task], return_when='FIRST_COMPLETED')
        if get_task in done:
            data, addr = await get_task
            if data == settings.udp_response:
                wait_task.cancel()
                return addr
            else:
                get_task = asyncio.create_task(loop.sock_recvfrom(udp_sock, 1024))
                continue
        else:
            get_task.cancel()
            return None


async def udp_requester():
    """
    Корутина для поиска сервера в локальной сети. Возвращает адрес найденного сервера. Если не найден - None.
    Нарочно не использует asyncio.timeout из-за проблем с отменой sock_recvfrom и выводом ошибок после прекращения работы программы
    """
    udp_sock = s.socket(s.AF_INET, s.SOCK_DGRAM)
    udp_sock.setsockopt(s.SOL_SOCKET, s.SO_BROADCAST, 1)
    udp_sock.setblocking(False)
    timer = asyncio.create_task(asyncio.sleep(settings.udp_wait_time))
    worker = asyncio.create_task(send_and_recv(udp_sock))
    try:
        while True:
            done, _ = await asyncio.wait([timer, worker], return_when='FIRST_COMPLETED')
            if worker in done:
                if worker.result():
                    return worker.result()
                else:
                    worker = asyncio.create_task(send_and_recv(udp_sock))
                    continue
            else:
                worker.cancel()
                return None
    finally:
        udp_sock.close()


async def is_there_running_server():
    """
    Корутина проверяет существование сервера в локальной сети и возвращает True, если сервер найден, иначе False.
    """
    return bool(await udp_requester())
        

if __name__ == '__main__':
    print(asyncio.run(is_there_running_server()))