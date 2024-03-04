import asyncio
import random
import datetime
import logging

logging.basicConfig(
    filename='server_log.txt',
    level=logging.INFO,
    format='%(asctime)s;%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

clients = []
response_counter = 0


async def handle_client(reader, writer):
    global response_counter
    addr = writer.get_extra_info('peername')
    client_id = len(clients) + 1
    clients.append((client_id, writer))
    print(f"Подключен клиент {addr}")

    try:
        while True:
            data = await reader.readline()
            if data == b'':
                print(f"Клиент {addr} отключился")
                break
            message = data.decode().strip()
            print(f"Получено сообщение от {addr}: {message}")

            # Логируем получение сообщения
            logging.info(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S};{message};")

            # Игнорирование сообщения с вероятностью 10%
            if random.randint(1, 10) == 1:
                print(f"Сообщение от {addr} проигнорировано")
                # Логируем игнорирование сообщения
                logging.info(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S};{message};(ignored)")
                continue

            # Засекаем случайный интервал от 100 до 1000 мс
            await asyncio.sleep(random.uniform(0.1, 1.0))

            # Отправляем ответ клиенту
            response = f"[{response_counter}/{message[1:]}] PONG ({client_id})\n"
            writer.write(response.encode())
            await writer.drain()
            response_counter += 1
            print(f"Ответ отправлен клиенту {addr}: {response.strip()}")

            # Логируем отправку ответа
            logging.info(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S};{message};{response.strip()}")
    finally:
        clients.remove((client_id, writer))
        writer.close()
        await writer.wait_closed()


async def send_keepalive():
    global response_counter
    while True:
        await asyncio.sleep(5)
        for client_id, writer in clients:
            keepalive_message = f"[{response_counter}] keepalive\n"
            writer.write(keepalive_message.encode())
            await writer.drain()
            response_counter += 1
            print(f"Keepalive отправлен клиенту с ID {client_id}")


async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    addr = server.sockets[0].getsockname()
    print(f'Сервер слушает {addr}')

    # Запускаем задачу для рассылки keepalive сообщений
    keepalive_task = asyncio.create_task(send_keepalive())

    async with server:
        await server.serve_forever()


asyncio.run(main())
