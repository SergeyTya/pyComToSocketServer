from asyncio import get_event_loop
from serial_asyncio import open_serial_connection


async def run():
    reader, writer = await open_serial_connection(url='COM4', baudrate=230400)
    writer.write(bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x05, 0x85, 0xC9]))
    while True:
        line = await reader.read()
        print('data received', repr(line))


loop = get_event_loop()
loop.run_until_complete(run())