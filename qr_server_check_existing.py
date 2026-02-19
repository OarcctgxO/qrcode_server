import socket as s
import asyncio

import settings


async def udp_requester():
    loop = asyncio.get_running_loop()
    udp_sock = s.socket(s.AF_INET, s.SOCK_DGRAM)
    udp_sock.setsockopt(s.SOL_SOCKET, s.SO_BROADCAST, 1)
    udp_sock.setblocking(False)
    try:
        async with asyncio.timeout(settings.udp_wait_time):
            while True:
                await loop.sock_sendto(udp_sock, settings.udp_request, settings.broadcast_addr)
                wait_task = asyncio.create_task(asyncio.sleep(1))
                while True:
                    get_task = asyncio.create_task(loop.sock_recvfrom(udp_sock, 64))
                    done, _ = await asyncio.wait([get_task, wait_task], return_when="FIRST_COMPLETED")
                    if not get_task in done:
                        get_task.cancel()
                        break
                    else:
                        if (await get_task)[0] == settings.udp_response:
                            return (await get_task)[1]
                        else:
                            continue
    except asyncio.TimeoutError as er:
        new_error = asyncio.TimeoutError('Нет ответа от UDP-сервера')
        raise new_error from er
    finally:
        udp_sock.close()


async def is_there_running_server():
    try:
        await udp_requester()
        return True
    except asyncio.TimeoutError:
        return False
        

if __name__ == '__main__':
    print(asyncio.run(is_there_running_server()))