import asyncio
import serial_asyncio
import utilities as util
from serial_asyncio import open_serial_connection
import json
import server_cmd as adapter


def log(mes:str):
    mes ="{}: {}".format(str(loop.time()), mes)
    if loop.log_enable: print(mes)
    

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
        log("--> " + mes)
        if mes is not None:
            loop.create_task(com_reader(self.transport, mes))

async def com_reader(socket_transport, data:str):
    req = adapter.Builder.build_frame(data)
    if req is None: 
        return 
    if req.cmd == adapter.Iframe.Frame_types.ERROR:
        socket_transport.write(req.get_socket_response_frame().encode())
        return
    await loop.sts.lock.acquire()
    try:
        start_time = loop.time()
        log("--> " + str(req.load_data_to_serial()))
        loop.sts.writer.write(req.load_data_to_serial())
        await asyncio.sleep(0.035)
        deadline = loop.time() + 1
        try:
            async with asyncio.timeout_at(deadline):
                res = await loop.sts.reader.read(256)
                if loop.log_enable: print(res)
                log("<-- " + str(res))
        except TimeoutError:
                res = "Timeout"
                log("Serial port time out")
        except PermissionError:
                log("Port error")
    finally:
        loop.sts.lock.release()   

    # response to socket
    if type(res) is str:
        socket_transport.write(res.encode())
    elif type(res) is bytes:
        frame = req.load_response_from_serial(res)
        if frame is not None:
            socket_transport.write(frame.encode())
            log("<-- " + frame)
        else:
            socket_transport.write("crc fault".encode())
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

async def start_server(loop=None, com_name='COM5', com_speed=230400,ip = 'localhost', port=8888 ):
    if loop is None:
        loop = asyncio.get_event_loop()

    serial_to_socket = SerialToSocketServer()
    loop.sts = serial_to_socket

    loop.log_enable = True
    await start_serial_server(loop, com_name, com_speed)
    await start_socket_server(loop, ip, port)

loop = asyncio.get_event_loop()
loop.run_until_complete(start_server())
loop.run_forever()
loop.close()
