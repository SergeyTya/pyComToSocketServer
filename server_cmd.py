
import json
import utilities as util

class ServerFrame(object):

    def read(data: bytes):
        if data is None : return data
        ServerFrame.read(data.decode())

    def read(data: str):
        if data is None : return data
        try:
            res = json.loads(data)
            obj = ServerFrame(**res)
            obj.add_crc()
        except TypeError: 
             return None
        except json.JSONDecodeError: 
            print(data)
            return None
        
        return obj
    
    def load_raw(data: bytes):
        crc = util.check_CRC_frame(data)
        if crc:
            res = "{'cmd': 'RAW' , 'data': " +  str(list((data)))  + " }"
            return ( res ).encode()
        else:
            return None

    def __init__(self, cmd, data:list):
        self.cmd = cmd
        self.data = data
        self.crc = util.computeCRC(data)

    def add_crc(self):
        self.data_with_crc = self.data
        self.data_with_crc.append((0xFF00&self.crc)>>8)
        self.data_with_crc.append(0x00FF&self.crc)
