import asyncio
import random
import datetime
import logging

client_id = 1
logging.basicConfig(
    filename=f'client_{client_id}_log.txt',
    level=logging.INFO,
    format='%(asctime)s;%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


async def tcp_client(client_id, server_ip, server_port):
    # Настройка логгера для каждого клиента
    logger = logging.getLogger(f'Client{client_id}')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(f'client_{client_id}_log.txt')
    formatter = logging.Formatter('%(asctime)s;%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    reader, writer = await asyncio.open_connection(server_ip, server_port)
    print(f'Клиент {client_id} подключен к серверу {server_ip}:{server_port}')

    request_counter = 0
    try:
        while True:
            # Отправляем сообщение серверу
            message = f"[{request_counter}] PING"
            send_time = datetime.datetime.now()  # Фиксируем время отправки
            writer.write(message.encode() + b'\n')
            await writer.drain()
            print(f'Клиент {client_id} отправил: {message}')
            logger.info(f"{send_time:%Y-%m-%d %H:%M:%S};{message};")

            # Ждём ответа от сервера
            try:
                response = await asyncio.wait_for(reader.readline(), timeout=5.0)
                response = response.decode().strip()
                receive_time = datetime.datetime.now()  # Фиксируем время получения ответа
                if response:
                    print(f'Клиент {client_id} получил: {response}')
                    logger.info(f";{response};{receive_time:%Y-%m-%d %H:%M:%S}")
            except asyncio.TimeoutError:
                receive_time = datetime.datetime.now()  # Фиксируем время таймаута
                print(f'Клиент {client_id} не получил ответ в течение таймаута')
                logger.info(f";(timeout);{receive_time:%Y-%m-%d %H:%M:%S}")

            # Случайный интервал от 300 до 3000 мс
            await asyncio.sleep(random.uniform(0.3, 3.0))
            request_counter += 1
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    server_ip = '127.0.0.1'
    server_port = 8888

    # Запускаем двух клиентов
    tasks = []
    for i in range(1, 3):
        task = asyncio.create_task(tcp_client(i, server_ip, server_port))
        tasks.append(task)

    # Запускаем клиентов на 5 минут
    await asyncio.sleep(300)

    # Отменяем задачи клиентов и ждём их завершения
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


asyncio.run(main())
