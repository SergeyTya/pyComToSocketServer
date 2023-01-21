import asyncio
import utilities as util

class EchoClientProtocol(asyncio.Protocol):

    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        self.tr = transport
        transport.write(self.message.encode())
        print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        print("--->" + str(data))

    def connection_lost(self, exc):
        print('The server closed the connection')
        self.on_con_lost.set_result(True)

    def resume_writing(self, exc):
        self.tr.write(self.message)

async def client():
    message = ' type raw '
    transport, protocol = await loop.create_connection(
        lambda: EchoClientProtocol(message, on_con_lost),
        '127.0.0.1', 8888)
    loop.create_task(wait_for_con_lost(transport))

    while True:
        req = bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x05, 0x85, 0xC9])
        protocol.message = req
        protocol.resume_writing(transport)
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

