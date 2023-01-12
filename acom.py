import asyncio
import serial_asyncio
from serial_asyncio import open_serial_connection

lock = asyncio.Lock()


async def com_writer():
    reader, writer = await open_serial_connection(loop=loop, url='COM4', baudrate=230400)
    while True:
        if lock.locked():
            await asyncio.sleep(0.03)
            n = n + 1
        else:
            await lock.acquire()
            try:
                writer.write(bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x05, 0x85, 0xC9]))
                deadline = loop.time() + 1
                try:
                    async with asyncio.timeout_at(deadline):
                        line = await reader.read(256)
                except TimeoutError:
                    print("The long operation timed out, but we've handled it.")
            finally:

                lock.release()


loop = asyncio.get_event_loop()
loop.create_task(com_writer())
loop.run_forever()
loop.close()