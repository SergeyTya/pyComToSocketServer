import asyncio
import serial_asyncio


lock = asyncio.Lock()

class OutputProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        # print('port opened', transport)
        transport.serial.rts = False  # You can manipulate Serial object via transport
        # transport.write(bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x05, 0x85, 0xC9]))
      
          # Write serial data via transport

    def data_received(self, data):
        # print('data received', repr(data))
        self.transport.close()
        lock.release()
       

    # def connection_lost(self, exc):
    #     print('port closed')
    #     # self.transport.loop.stop()

    # def pause_writing(self):
    #     print('pause writing')
    #     print(self.transport.get_write_buffer_size())

    # def resume_writing(self):
    #     print(self.transport.get_write_buffer_size())
    #     print('resume writing')

async def com_writer(data):
    transport, protocol = await serial_asyncio.create_serial_connection(loop, OutputProtocol, 'COM4', baudrate=230400)
    transport.write(data)
    # while True:
    #     await asyncio.sleep(0.3)
    #     protocol.resume_reading()


async def cycle():
    cnt =0 
    while True:
        await lock.acquire()
        loop.create_task(com_writer(bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x05, 0x85, 0xC9])))


loop = asyncio.get_event_loop()
loop.run_until_complete(cycle())
loop.run_forever()
loop.close()