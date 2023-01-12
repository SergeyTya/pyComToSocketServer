import asyncio
from serial_asyncio import open_serial_connection

buf_trans = []
buf_data = []
lock = asyncio.Lock()


class EchoServerClientProtocol(asyncio.Protocol):
    transport = None

    def connection_made(self, transport):
        self.transport = transport
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))

    def data_received(self, data):
        mes = str(data, "utf-8").rstrip()
        if (len(mes)) > 0:
            loop.create_task(dputer(self.transport, mes))


async def dputer(transport, mes):
    await lock.acquire()
    try:
        buf_trans.append(transport)
        buf_data.append(mes)
    finally:
        lock.release()


async def com_communicate():
    reader, writer = await open_serial_connection(loop=loop, url='COM4', baudrate=230400)
    print('com connected')
    while True:
        await lock.acquire()
        try:
            if len(buf_trans) > 0:
                transport = buf_trans.pop()

                if len(buf_trans) > 100:
                    for x in range(len(buf_trans)):
                        buf_trans[x].write("Server_buisy".encode())
                    buf_trans.clear()
                    buf_data.clear()
                    continue

                mes = buf_data.pop()
                # writer.write(bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x05, 0x85, 0xC9]))
                writer.write(bytes([0x01, 0x14, 0x00, 0x2F])) # scope
                deadline = loop.time() + 1
                try:
                    async with asyncio.timeout_at(deadline):
                        line = await reader.read(256)
                        print(line)
                        transport.write(('ok-> ' + mes + "\n").encode())
                except TimeoutError:
                    print("The long operation timed out, but we've handled it.")
                    transport.write(('TO-> ' + mes + "\n").encode())
        finally:
            await asyncio.sleep(0.025)
            lock.release()




loop = asyncio.get_event_loop()
coro_socket = loop.create_server(EchoServerClientProtocol, '127.0.0.1', 8888)
loop.create_task(com_communicate())
server = loop.run_until_complete(coro_socket)


# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()