import asyncio
import serial_asyncio
import utilities as util
from serial_asyncio import open_serial_connection
import json


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
        # mes = str(data, "utf-8").rstrip()
        if data is not None:
            loop.create_task(RTU_to_TCP_converter(self.transport, data))

async def RTU_to_TCP_converter(socket_transport, data):

    try:
        expected_pdu_len = data[5] + (data[4]<<8) +6
        if expected_pdu_len != len(data): raise RuntimeError
    except Exception:
        log("Socket: MODBUS TCP frame error")
        return

    log("Socket:input: " + str(bytes(data)))

    header = data[:6]
    body = list(data[6:])
    crc =util.computeCRC(body)
    body.append((0xFF00&crc)>>8)
    body.append(0x00FF&crc)

    await loop.sts.lock.acquire()
    try:
        loop.sts.writer.write(bytes(body))
        await asyncio.sleep(0.035)
        deadline = loop.time() + 1
        try:
            async with asyncio.timeout_at(deadline):
                res = await loop.sts.reader.read(256)
                log("Serial:input: " + str(res))
                body = res[:len(res)-2]
                header[4] = (0xFF00&len(body))>>8
                header[5] = len(body)&0xff
                packet = list(header)
                body = list(body)
                packet = packet + body
                packet = bytes(packet)
                log("Socket:output: " + str(packet) )
                socket_transport.write(packet)
        except TimeoutError:
                log("Serial: Time out")
        except PermissionError:
                log("Serial: Port error")
    finally:
        loop.sts.lock.release()   

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

    loop.log_enable = False
    await start_serial_server(loop, com_name, com_speed)
    await start_socket_server(loop, ip, port)

loop = asyncio.get_event_loop()
loop.run_until_complete(start_server())
loop.run_forever()
loop.close()
