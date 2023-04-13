import asyncio
import os
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
    com_name = ""
    com_speed=0


def log(mes:str):
    mes ="{}: {}".format(str(loop.time()), mes)
    if loop.log_enable: print(mes)

def shutdown():
    """Performs a clean shutdown"""
    log('received sys os stop')
    os._exit(-1)
        
class SocketServerProtocol(asyncio.Protocol):

    client_type = [   
        "raw", 
        "modbus",
        "listener"
    ]

    def parse(self, mes):
        res= shlex.split(mes)
        res = list(res)
        try:
            if 'type' in res:
                tp = res[res.index('type')+1]
                if tp in self.client_type:
                    self.type = tp
                    if self.type == self.client_type[2]:
                        if self.transport not in loop.listeners:
                            loop.listeners.append(self.transport)

                    return 'done'
            if 'info' in res:
                return "{}:{}".format(loop.sts.com_name, str(loop.sts.com_speed))
        except IndexError: pass

    def connection_made(self, transport):
        self.type = self.client_type[1]
        self.transport = transport
        peer = self.transport.get_extra_info('peername')
        print('Connection from {}'.format("{} {}".format(peer[0],peer[1])))

    def data_received(self, data):
        if data is None:
            return
        try:
            mes = data.decode()
            if mes == "close": 
                shutdown()
            if mes == "version": 
               self.transport.write("v.0.0.1".encode())
               return
            cmd = self.parse(mes)
            if cmd is not None:
                self.transport.write(cmd.encode())
                return
        except UnicodeDecodeError: pass
        except ValueError:         pass

        if self.type == self.client_type[0]:
            loop.create_task(RAW_converter(self.transport, data))

        if self.type == self.client_type[1]:
            loop.create_task(Modbus_converter(self.transport, data))
        
       
    def connection_lost(self, exec):
        peername = self.transport.get_extra_info('peername')
        print('Connection closed {}'.format(peername))
        try:    
            if self.transport in loop.listeners:
                loop.listeners.remove(self.transport)
        except TypeError:
            pass


 

async def Modbus_converter(socket_transport, data):
    log("----------")
    log("Socket:read: " + str(list(data)))

    try:
        expected_pdu_len = data[5] + (data[4]<<8) +6
        if expected_pdu_len != len(data): raise RuntimeError
    except Exception:
        mes = "Socket: MODBUS TCP frame error"
        log(mes)
        socket_transport.write(mes.encode())
        print(mes)
        return
    
    header = list(data[:6])
    body = list(data[6:])
    crc =util.computeCRC(body)
    body.append((0xFF00&crc)>>8)
    body.append(0x00FF&crc)

    await loop.sts.lock.acquire()
    try:
        log("Serial:write: " + str(body))
        loop.sts.writer.write(bytes(body))
        await asyncio.sleep(0.045)
        deadline = loop.time() + 1
        try:
            async def temp_foo():
                res = await loop.sts.reader.read(256)
                log("Serial:read: " + str(list(res)))
                if util.check_CRC_frame(res) == False:
                    mes = "Serial: CRC error"
                    log(mes)
                    socket_transport.write(mes.encode())
                else:
                    body = res[:len(res)-2]
                    header[4] = (0xFF00&len(body))>>8
                    header[5] = len(body)&0xff
                    packet = list(header)
                    body = list(body)
                    packet = packet + body
                    packet = bytes(packet)
                    log("Socket:write: " + str(list(packet)) )
                    socket_transport.write(packet)
                    for listener in loop.listeners:
                        listener.write(res)
      
            await asyncio.wait_for(temp_foo(), timeout=0.1)

        except asyncio.TimeoutError:
                mes = "Serial: Time out"
                log(mes)
                socket_transport.write(mes.encode())
                print(mes)
        except PermissionError:
                mes = "Serial: Port error"
                log(mes)
                socket_transport.write(mes.encode())
                print(mes)
        except  Exception:
                mes = "Serial: Unexpected error"
                socket_transport.write(mes.encode())
                print(mes)
    finally:
        loop.sts.lock.release()  

async def RAW_converter(socket_transport, data):

    if data == None:
        log("Socket:empty request")
        return

    log("Socket:input: " + str(bytes(data)))

    await loop.sts.lock.acquire()
    try:
        log("Serial:write: " + str(list(res)))
        loop.sts.writer.write(bytes(data))
        await asyncio.sleep(0.025)
        deadline = loop.time() + 1
        try:
            async def temp_foo_raw():
                res = await loop.sts.reader.read(256)
                log("Serial:read: " + str(list(res)))
                log("Socket:write: " + str(list(res)))
                socket_transport.write(res)
                for listener in loop.listeners:
                    listener.write(res)
            
            await asyncio.wait_for(temp_foo_raw(), timeout=1.0)
                
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

async def start_server(loop=None, com_name='COM5', com_speed=230400,ip = '124.0.0.1', port=8888 ):
    if loop is None:
        loop = asyncio.get_event_loop()
    serial_to_socket = SerialToSocketServer()
    serial_to_socket.com_name = com_name
    serial_to_socket.com_speed = com_speed
    loop.sts: SerialToSocketServer = serial_to_socket
    loop.log_enable: bool = False
    loop.listeners: list = []
    await start_serial_server(loop, com_name, com_speed)
    await start_socket_server(loop, ip, port)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", type=str, default="COM6"     , required=False )
    parser.add_argument("--speed" , type=int, default=9600       , required=False )
    parser.add_argument("--host"  , type=str, default="localhost", required=False )
    parser.add_argument("--port"  , type=int, default=8888       , required=False )
    
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server(loop = loop, com_name=args.serial, com_speed=args.speed, ip=args.host, port=args.port ))
    loop.run_forever()
    loop.close()
