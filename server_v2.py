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
            loop.create_task(com_reader(self.transport, "mes") )


class ComServerProtocol(asyncio.Protocol):

    serial_lock = asyncio.Lock()
    res = 0

    def connection_made(self, transport):
        self.transport = transport
        print('port opened', transport)
          
    def data_received(self, data):
        # print('data received', repr(data))
        self.res = data
        self.serial_lock.release()

    def pause_writing(self):
        print('pause writing')
      
    async def write_data(self, data):
        deadline = loop.time() + 0.1
        try:
            async with asyncio.timeout_at(deadline):
                await self.serial_lock.acquire()
                try:
                    await asyncio.sleep(0.05)
                    self.transport.write(data)
                finally:
                    pass
        except TimeoutError:
            return 0
        return self.res
        
        
async def com_reader(socket_transport, data):         
    res = await serial_protocol.write_data(bytes([0x01, 0x14, 0x00, 0x2F]))
    print(res)    
    socket_transport.write("done".encode())


loop = asyncio.get_event_loop()
coro_socket = loop.create_server(SocketServerProtocol, '127.0.0.1', 8888)
coro_com = serial_asyncio.create_serial_connection(loop, ComServerProtocol, 'COM5', baudrate=115200)

serial_transport, serial_protocol = loop.run_until_complete(coro_com)
server = loop.run_until_complete(coro_socket)
print('Serving on {}'.format(server.sockets[0].getsockname()))
loop.run_forever()
loop.close()