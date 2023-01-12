import asyncio
import serial_asyncio


lock = asyncio.Lock()

class OutputProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        transport.serial.rts = False  # You can manipulate Serial object via transport

    def data_received(self, data):
        try:
            lock.release()
        except RuntimeError:
            pass

    def pause_writing(self):
        print('pause writing')
        print(self.transport.get_write_buffer_size())

    def resume_writing(self):
        print(self.transport.get_write_buffer_size())
        print('resume writing')

async def com_writer(data):
    while True:
        transport, protocol = await serial_asyncio.create_serial_connection(loop, OutputProtocol, 'COM4', baudrate=230400)
        n = 0
        while n<10:
            if lock.locked():
                await asyncio.sleep(0.03)
                n = n + 1
            else:
                await lock.acquire()
                n = 0
                transport.write(bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x05, 0x85, 0xC9]))
        n=0
        transport.close()
        print('Timeout!')
        await asyncio.sleep(1)
        try:
            lock.release()
        except RuntimeError:
            pass


loop = asyncio.get_event_loop()
loop.run_until_complete(com_writer(0))
loop.run_forever()
loop.close()