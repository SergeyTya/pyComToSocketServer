import asyncio
import utilities as util

import json
from server_cmd import ServerFrame

lock = asyncio.Lock()




class EchoClientProtocol(asyncio.Protocol):

    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        self.tr = transport
        transport.write(self.message.encode())
        print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        # u = ServerFrame.read(data)
        print(data.decode())
        lock.release()

    def connection_lost(self, exc):
        print('The server closed the connection')
        self.on_con_lost.set_result(True)

    def resume_writing(self, exc):
        self.tr.write(self.message.encode())

async def client():
    message = ''
    transport, protocol = await loop.create_connection(
        lambda: EchoClientProtocol(message, on_con_lost),
        '127.0.0.1', 8888)
    loop.create_task(wait_for_con_lost(transport))
    while True:
        try:
            deadline = loop.time() + 0.1
            async with asyncio.timeout_at(deadline):
                await lock.acquire()
                try:
                    data = json.dumps({'cmd': 'RAW' , 'data': [0x01, 0x03, 0, 0, 0, 5]})
                    protocol.message =data
                    protocol.resume_writing(transport)
                finally:
                    pass
        except TimeoutError:
            print("Time out")
        await asyncio.sleep(0.50)



async def wait_for_con_lost(transport):
    try:
        await on_con_lost
    finally:
        transport.close()

loop = asyncio.get_event_loop()
on_con_lost = loop.create_future()
loop.create_task(client())
loop.run_forever()

