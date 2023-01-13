import asyncio

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
        print('Data received: {!r}'.format(data.decode()))
        lock.release()

    def connection_lost(self, exc):
        print('The server closed the connection')
        self.on_con_lost.set_result(True)

    def resume_writing(self, exc):
        print('resume')
        self.tr.write(self.message.encode())

async def client():
    message = 'Hello World!'
    transport, protocol = await loop.create_connection(
        lambda: EchoClientProtocol(message, on_con_lost),
        '127.0.0.1', 8888)
    loop.create_task(wait_for_con_lost(transport))
    while True:
        await lock.acquire()
        try:
            protocol.message = "next"
            protocol.resume_writing(transport)

        finally:
            pass
        await asyncio.sleep(0.050)



async def wait_for_con_lost(transport):
    try:
        await on_con_lost
    finally:
        transport.close()

loop = asyncio.get_event_loop()
on_con_lost = loop.create_future()
loop.create_task(client())
loop.run_forever()

