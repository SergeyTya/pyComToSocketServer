import asyncio
import serial_asyncio
import utilities as util
from serial_asyncio import open_serial_connection
import sys
import argparse
import shlex

class SerialToSocketServer:
    writer = None
    reader = None
    server = None
    lock   = None


def log(mes:str):
    mes ="{}: {}".format(str(loop.time()), mes)
    if loop.log_enable: print(mes)
    
class SocketServerProtocol(asyncio.Protocol):

    class Client_type:
        MODBUS   = "modbus"
        RAW      = "raw"
        LISTENER = "listener"
        DEFAULT  = ""
        
    type:Client_type = Client_type.MODBUS

    def parse(self, mes):
        res= shlex.split(mes)
        res = list(res)
        try:
            if 'type' in res:
                tp = res[res.index('type')+1]
                if tp == self.Client_type.LISTENER: 
                    return self.Client_type.LISTENER
                if tp == self.Client_type.RAW:    
                    return self.Client_type.RAW
                if tp == self.Client_type.MODBUS:  
                     return self.Client_type.MODBUS
                return self.Client_type.DEFAULT
        except IndexError: pass

    def connection_made(self, transport):
        self.transport = transport
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))

    def data_received(self, data):
        if data is None:
            return
        try:
            mes = data.decode()
            tp = self.parse(mes)
            log(tp)
            if tp is not None:
                if tp is not self.Client_type.DEFAULT:
                    self.type = tp
                    log  ("setup client type " + str(tp))
                    print("Setup client type " + str(tp))
                else:
                    self.transport.write(shlex.join([self.Client_type.MODBUS , self.Client_type.RAW, self.Client_type.LISTENER]).encode())
                # add listener client
                if self.type is self.Client_type.LISTENER:
                    if self.transport not in loop.listeners:
                        loop.listeners.append(self.transport)
                else:
                    if self.transport in loop.listeners:
                        loop.listeners.remove(self.transport)
                self.transport.write("done".encode())
                return
        except UnicodeDecodeError: pass
        except ValueError:         pass

        if self.type is self.Client_type.MODBUS:
            loop.create_task(Modbus_converter(self.transport, data))
           
        if self.type is self.Client_type.RAW:
            loop.create_task(RAW_converter(self.transport, data))
            
        
    def connection_lost(self, exec):
        peername = self.transport.get_extra_info('peername')
        print('Connection closed {}'.format(peername))
        try:    
            if self.transport in loop.listeners:
                loop.listeners.remove(self.transport)
        except TypeError:
            pass

async def Modbus_converter(socket_transport, data):

    try:
        expected_pdu_len = data[5] + (data[4]<<8) +6
        if expected_pdu_len != len(data): raise RuntimeError
    except Exception:
        log("Socket: MODBUS TCP frame error")
        socket_transport.write("err".encode())
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
                for listener in loop.listeners:
                    listener.write(res)
        except TimeoutError:
                log("Serial: Time out")
        except PermissionError:
                log("Serial: Port error")
    finally:
        loop.sts.lock.release()  

async def RAW_converter(socket_transport, data):

    if data == None:
        log("Socket:empty request")
        return

    log("Socket:input: " + str(bytes(data)))

    await loop.sts.lock.acquire()
    try:
        loop.sts.writer.write(bytes(data))
        await asyncio.sleep(0.035)
        deadline = loop.time() + 1
        try:
            async with asyncio.timeout_at(deadline):
                res = await loop.sts.reader.read(256)
                log("Serial:input: " + str(res))
                log("Socket:output: " + str(res) )
                socket_transport.write(res)
                for listener in loop.listeners:
                    listener.write(res)
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
    print('Serving Serial on {}:{}'.format(com_name, com_speed))
    loop.sts.writer = writer
    loop.sts.reader = reader
    loop.sts.lock = asyncio.Lock()
    return reader, writer

async def start_server(loop=None, com_name='COM5', com_speed=230400,ip = 'localhost', port=8888 ):
    if loop is None:
        loop = asyncio.get_event_loop()
    serial_to_socket = SerialToSocketServer()
    loop.sts: SerialToSocketServer = serial_to_socket
    loop.log_enable: bool = False
    loop.listeners: list = []
    await start_serial_server(loop, com_name, com_speed)
    await start_socket_server(loop, ip, port)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", type=str, default="COM5"     , required=False )
    parser.add_argument("--speed" , type=int, default=9600       , required=False )
    parser.add_argument("--host"  , type=str, default="localhost", required=False )
    parser.add_argument("--port"  , type=int, default=8888       , required=False )
    
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server(loop = loop, com_name=args.serial, com_speed=args.speed, ip=args.host, port=args.port ))
    loop.run_forever()
    loop.close()
