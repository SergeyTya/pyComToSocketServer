import asyncio
import serial_asyncio
import utilities as util
from serial_asyncio import open_serial_connection
import json
from server_cmd import ServerFrame

class SerialToSocketServer:
    writer = None
    reader = None
    server = None
    lock   = None

    def __init__(self):
        pass

class SocketServerProtocol(asyncio.Protocol):
    transport = None
    def connection_made(self, transport):
        self.transport = transport
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))

    def data_received(self, data):
        mes = str(data, "utf-8").rstrip()
        res = ServerFrame.read(mes)
        if res is not None:
            loop.create_task(com_reader(self.transport, bytes(res.data_with_crc)))

async def com_reader(socket_transport, data:bytes):
    await loop.sts.lock.acquire()
    try:
        start_time = loop.time()
        # loop.sts.writer.write(bytes([0x01, 0x14, 0x00, 0x2F]))
        loop.sts.writer.write(data)
        await asyncio.sleep(0.035)
        deadline = loop.time() + 1
        try:
            async with asyncio.timeout_at(deadline):
                res = await loop.sts.reader.read(256)
        except TimeoutError:
                res = "Timeout"
                print(res)
    finally:
        loop.sts.lock.release()   

    # response to socket
    if type(res) is str:
        socket_transport.write(res.encode())
    elif type(res) is bytes:
        raw_frm = ServerFrame.load_raw(res)
        if raw_frm is not None:
            socket_transport.write(raw_frm)
        else:
            socket_transport.write("crc fault".encode())

        
        # if util.check_CRC_frame(res):
        #     socket_transport.write("crc ok".encode())
        # else: 
        #     socket_transport.write("crc fault".encode())
        #     print("crc fault")
    else:
        socket_transport.write("wrong frame".encode())
        print(type(res))

async def start_socket_server(loop=None, ip = 'localhost', port=8888):
    if loop is None:
        loop = asyncio.get_event_loop()
    server = await loop.create_server(SocketServerProtocol, ip, port)
    print('Serving Socket on {}:{}'.format(ip, port))
    loop.sts.server = server
    return server

async def start_serial_server(loop=None, com_name='COM4', com_speed=230400):
    if loop is None:
        loop = asyncio.get_event_loop()
    reader, writer = await open_serial_connection(loop=loop, url=com_name, baudrate=com_speed)
    print('Serving Serial Port on {} {}'.format(com_name, com_speed))
    loop.sts.writer = writer
    loop.sts.reader = reader
    loop.sts.lock = asyncio.Lock()
    return reader, writer

async def start_server(loop=None, com_name='COM4', com_speed=230400,ip = 'localhost', port=8888 ):
    if loop is None:
        loop = asyncio.get_event_loop()

    serial_to_socket = SerialToSocketServer()
    loop.sts = serial_to_socket

    await start_serial_server(loop, com_name, com_speed)
    await start_socket_server(loop, ip, port)

loop = asyncio.get_event_loop()
loop.run_until_complete(start_server())
loop.run_forever()
loop.close()
