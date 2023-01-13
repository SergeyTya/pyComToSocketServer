import asyncio
import serial_asyncio


class SocketServerProtocol(asyncio.Protocol):
    transport = None

    def connection_made(self, transport):
        self.transport = transport
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))

    def data_received(self, data):
        mes = str(data, "utf-8").rstrip()
        if (len(mes)) > 0:
            loop.create_task(com_reader(self.transport, "mes"))


class ComServerProtocol(asyncio.Protocol):

    serial_lock = asyncio.Lock()
    res = 0
    time_elapsed = 0

    def release_lock(self):
        try:
            self.serial_lock.release()
        except RuntimeError:
            pass

    def connection_made(self, transport):
        self.transport = transport
        print('port opened', transport)

    def data_received(self, data):
        # print('data received', repr(data))
        self.res = data
        self.release_lock()

    def pause_writing(self):
        print('pause writing')

    async def write_data(self, data):
        deadline = loop.time() + 1.0
        try:
            async with asyncio.timeout_at(deadline):
                await self.serial_lock.acquire()
                try:
                    print(loop.time() - self.time_elapsed)
                    self.transport.write(data)
                finally:
                    await asyncio.sleep(0.05)
        except TimeoutError:
            self.release_lock()
            return "Time out"
        self.time_elapsed = loop.time()
        return self.res


async def com_reader(socket_transport, data):
    res = await serial_protocol.write_data(bytes([0x01, 0x14, 0x00, 0x2F]))
    if type(res) is str:
        socket_transport.write(res.encode())
    else:
        socket_transport.write("done".encode())


loop = asyncio.get_event_loop()
coro_socket = loop.create_server(SocketServerProtocol, '127.0.0.1', 8888)
coro_com = serial_asyncio.create_serial_connection(
    loop, ComServerProtocol, 'COM4', baudrate=230400)

serial_transport, serial_protocol = loop.run_until_complete(coro_com)
server = loop.run_until_complete(coro_socket)
print('Serving on {}'.format(server.sockets[0].getsockname()))
loop.run_forever()
loop.close()
