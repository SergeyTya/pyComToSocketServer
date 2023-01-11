import asyncio
from serial_asyncio import open_serial_connection


# buf = []
# lock = asyncio.Lock()

# def readMes(mes):
#     if len(mes) > 5:
#         print('<-:{!r}'.format(message))
#         loop.create_task(writeToBuf([1, 3, 0, 0, 5, 0x85, 0xCD]))
#     pass

# async def writeToBuf(data):
#     async with lock:
#         print('socket acquired lock')
#         buf.append(data)

# class EchoServerClientProtocol(asyncio.Protocol):
#     tran = None
#     def connection_made(self, transport):
#         self.tran = transport
#         peername = transport.get_extra_info('peername')
#         print('Connection from {}'.format(peername))
#         self.transport = transport

#     def data_received(self, data):
#         nm= self.tran.get_extra_info('peername')
#         message = data.decode()
#         # print('From:{!r}'.format(nm))
#         # self.transport.write(('Echoed back: {}'.format(message)).encode())
#         readMes(message)

    

async def run():
    reader, writer = await open_serial_connection(url='COM4', baudrate=230400)
    while True:
        # # await lock.acquire()
        # try:
        #     # print('com acquired lock')
        #     # 
        #     # print(str(line, 'utf-8'))
        #     # asyncio.sleep(10)
        #     if len (buf) != 0:
        #         print("->")
        #         writer.write([1, 3, 0, 0, 5, 0x85, 0xCD])
        # finally:
        #     # print('com released lock')
        #     lock.release()
        # writer.write([1, 3, 0, 0, 5, 0x85, 0xCD])
        # await asyncio.sleep(1)
        line = await reader.readline()
        print(line)


       

loop = asyncio.get_event_loop()
# coro_socket = loop.create_server(EchoServerClientProtocol, '127.0.0.1', 8888)
# server = loop.run_until_complete(coro_socket)
loop.run_until_complete(run())


# # Serve requests until Ctrl+C is pressed
# print('Serving on {}'.format(server.sockets[0].getsockname()))
# try:
#     loop.run_forever()
# except KeyboardInterrupt:
#     pass

# # Close the server
# server.close()
# loop.run_until_complete(server.wait_closed())
# loop.close()