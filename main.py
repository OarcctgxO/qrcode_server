import asyncio
import concurrent.futures
import sys, os

import settings
from qr_server_udp_discover import UdpDiscoverer
from qr_server_cpu import make_qr_code
from qr_server_check_existing import is_there_running_server


#PyInstaller + multiprocessing
if getattr(sys, 'frozen', False):
    import multiprocessing
    multiprocessing.freeze_support()
    os.environ['MULTIPROCESSING_METHOD'] = 'spawn'


class MainServer:
    """
    Главный класс сервера. Запускает UDP и TCP сервер, запускает задачи на генерацию QR-кодов
    """
    def __init__(self):
        self.udp_server: UdpDiscoverer
        self.cpu_exec = concurrent.futures.ProcessPoolExecutor()
        
        self.tcp_server: asyncio.Server
    
    async def client_handler(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        print('Новое TCP подключение. Жду строки текста.')
        loop = asyncio.get_running_loop()
        
        try:
            data = await reader.read(10240)
            try:
                texts = data.decode('utf-8').split('\n')
            except UnicodeDecodeError:
                texts = data.decode('windows-1251').split('\n')
            texts = [text for text in texts if text] #purge empty strings
            print(f'Получено строк вот столько: {len(texts)}. Перечисление:')
            print(*texts)
            future_list = []
            if len(texts) >= settings.thread_pool_limit:
                for s in texts:
                    future_qr = loop.run_in_executor(self.cpu_exec, make_qr_code, s)
                    future_list.append(future_qr)
            else:
                for s in texts:
                    task_qr = asyncio.create_task(asyncio.to_thread(make_qr_code, s))
                    future_list.append(task_qr)
            
            counter = 1
            result = ''
            for f in future_list:
                res = await f
                print(f'Сформирован qr-код и закодирован в base64 - строка {counter}')
                result = '\n'.join((result, res)) if result else res
                counter += 1
            
            print('Все коды готовы, начинаю отправку.')
            writer.write(result.encode('ascii'))
            await writer.drain()
            print('Все коды отправлены, закрываю соединение.')
        except Exception as er:
            print(repr(er))
        finally:
            writer.close()
        
    
    async def close(self):
        if hasattr(self, 'udp_server') and self.udp_server:
            self.udp_server.close()
        if hasattr(self, 'tcp_server') and self.tcp_server:
            print("TCP сервер получает запрос на отмену...")
            self.tcp_server.close()
            await self.tcp_server.wait_closed()
            print("TCP сервер завершил работу.")
        self.cpu_exec.shutdown(wait=False)
            
    
    async def start_server(self):
        try:
            self.udp_server = UdpDiscoverer()
            self.tcp_server = await asyncio.start_server(self.client_handler, *settings.server_addr, reuse_address=True)
            task_udp = asyncio.create_task(self.udp_server.work())
            task_tcp = asyncio.create_task(self.tcp_server.serve_forever())
            print('Сервер qr-кодов успешно запущен.')
            await task_tcp
        finally:
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
        # уничтожение всего последующего вывода после отмены работы сервера
        black_hole = open(os.devnull, 'w')
        sys.stderr = black_hole
        sys.stdout = black_hole