import socket as s
import asyncio

import settings


async def send_and_recv(udp_sock: s.socket):
    """
    Корутина, отправляющаяя broadcast запрос и ожидающаяя правильного ответа 1 секунду. Возвращает адрес ответившего. Если нет ответа - None.
    """
    loop = asyncio.get_running_loop()
    await loop.sock_sendto(udp_sock, settings.udp_request, settings.broadcast_addr)
    get_task = asyncio.create_task(loop.sock_recvfrom(udp_sock, 1024))
    try:
        async with asyncio.timeout(1):
            while True:
                data, addr = await get_task
                if data == settings.udp_response:
                    return addr
                else:
                    get_task = asyncio.create_task(loop.sock_recvfrom(udp_sock, 1024))
                    continue
    except asyncio.TimeoutError:
        return None
    finally:
        get_task.cancel()
        await asyncio.gather(get_task, return_exceptions=True)


async def udp_requester():
    """
    Корутина для поиска сервера в локальной сети.
    В течении таймера settings.udp_wait_time повторно отправляет запросы и ждет ответа.
    Возвращает адрес найденного сервера. Если не найден - None.
    """
    udp_sock = s.socket(s.AF_INET, s.SOCK_DGRAM)
    udp_sock.setsockopt(s.SOL_SOCKET, s.SO_BROADCAST, 1)
    udp_sock.setblocking(False)

    worker = asyncio.create_task(send_and_recv(udp_sock))
    try:
        async with asyncio.timeout(settings.udp_wait_time):
            while True:
                if await worker:
                    return worker.result()
                else:
                    worker = asyncio.create_task(send_and_recv(udp_sock))
    except asyncio.TimeoutError:
        return None
    finally:
        worker.cancel()
        await asyncio.gather(worker, return_exceptions=True)
        udp_sock.close()


async def is_there_running_server():
    """
    Корутина проверяет существование сервера в локальной сети и возвращает True, если сервер найден, иначе False.
    """
    return bool(await udp_requester())
        

if __name__ == '__main__':
    print(asyncio.run(is_there_running_server()))