import asyncio
import concurrent.futures
import sys, os

import settings
from qr_server_udp_discover import UdpDiscoverer
from qr_server_cpu import make_qr_code
from qr_server_check_existing import is_there_running_server


class MainServer:
    """
    Главный класс сервера. Запускает UDP и TCP сервер, запускает задачи на генерацию QR-кодов
    """
    def __init__(self):
        self.udp_server = UdpDiscoverer()
        self.tcp_server: asyncio.Server
        self.cpu_exec = concurrent.futures.ThreadPoolExecutor(max_workers=settings.workers)

    
    async def client_handler(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        print('Открыто TCP-соединение. Жду строки текста:')
        loop = asyncio.get_running_loop()
        future_list = []
        try:
            try:
                async with asyncio.timeout(5):
                    while True:
                        data = await reader.readuntil(b'\n')
                        try:
                            text = data.decode('utf-8').rstrip('\n')
                        except UnicodeDecodeError:
                            text = data.decode('windows-1251').rstrip('\n')
                        
                        if not text:
                            print('\nПолучен сигнал конца сообщения - все строки получены.')
                            break
                        print(text, end=' ')
                        ftr = loop.run_in_executor(self.cpu_exec, make_qr_code, text)
                        future_list.append(ftr)
            except asyncio.TimeoutError:
                print('Таймаут получения данных: данных слишком много или клиент не отправляет сигнал конца сообщения (\\n\\n)')
            
            
            res = [await f for f in future_list]
            result = '\n'.join(res) + '\n\n'

            print(f'Готово кодов: {len(res)}. Начинаю отправку...')
            writer.write(result.encode('ascii'))
            await writer.drain()
            print('Все коды отправлены, закрываю соединение.')
            
        except Exception as er:
            print(repr(er))
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except ConnectionError:
                pass
        
    
    async def close(self):
        if hasattr(self, 'tcp_server') and self.tcp_server:
            print("TCP сервер получает запрос на отмену...")
            self.tcp_server.close()
            await self.tcp_server.wait_closed()
            print("TCP сервер завершил работу.")
        self.cpu_exec.shutdown(wait=False)
            
    
    async def start_server(self):
        self.tcp_server = await asyncio.start_server(self.client_handler, *settings.server_addr, reuse_address=True)
        task_udp = asyncio.create_task(self.udp_server.work())
        task_tcp = asyncio.create_task(self.tcp_server.serve_forever())
        print('Сервер qr-кодов успешно запущен.')
        try:
            done, _ = await asyncio.wait([task_tcp, task_udp], return_when="FIRST_COMPLETED")
            try:
                done.pop().result() # нет исключения - udp-запрос на завершение работы
            except:
                raise
        finally:
            task_udp.cancel()
            task_tcp.cancel()
            await self.close()

    
async def main():
    print("Поиск другого работающего сервера...")
    if (await is_there_running_server()):
        print("Найден другой работающий сервер в локальной сети. Завершаю работу...")
        input("Нажмите Enter.")
    else:
        print('Сервер не найден, новый сервер запускается...')
        await MainServer().start_server()
        

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        input("Штатное завершение работы через KeyboardInterrupt. Нажмите Enter")