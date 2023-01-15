from abc import abstractmethod
import json
import utilities as util

class Builder(object):

    def build_raw_request_with_crc(data:list): 
        """
        Create request frame for sending raw data to Serial port. \n
        Function automatic add CRC16 in the end of raw data. \n
        Return Iframe object
        """
        if data is None : return None
        crc = util.computeCRC(data)
        data_with_crc = data
        data_with_crc.append((0xFF00&crc)>>8)
        data_with_crc.append(0x00FF&crc)
        return RawFameReq(data_with_crc)

    def build_serialconnect_req(port_name, speed):
        
        return SerialConnectReq(port_name,speed)

    def build_frame(frame:str):
        obj = Iframe.read(frame)

        if obj.cmd == Iframe.Frame_types.RAW:
            return RawFameReq.create_from_Iframe(obj)
        if obj.cmd == Iframe.Frame_types.SERIAL_CONNECT:
            return SerialConnectReq.create_from_Iframe(obj)
        return obj

class Iframe(object):

    @abstractmethod
    def load_response_from_socket(self, frame: str) :
        """
        Use it when get data from socket \n
        return Iframe object             \n
        """
        raise NotImplementedError

    @abstractmethod
    def load_response_from_serial(self, data) -> str:
        """
        Use it when get data from serial \n
        return Iframe object             \n
        """
        raise NotImplementedError

    def load_data_to_serial(self) -> bytes:
        """
        Use it to get data for serial port
        """
        return self.get_serial_request_raw_frame()

    def load_request_to_socket(self) -> str:
        """
        Use it to get data for loading to client socket
        """
        return self.get_socket_request_frame()

    def load_response_to_socket(self) -> str:
        """
        Use it to get data for client socket
        """
        return self.get_socket_response_frame()

    def read(frame):
        if frame is None: return None
        try:
            res = json.loads(frame)
            obj = Iframe(**res)
        except TypeError:
            obj = ErrorFrame("TypeError") 
        except json.JSONDecodeError: 
            obj = ErrorFrame("JSONDecodeError")
        return obj

    def __init__(self, cmd=None, data=None) -> None:
        self.__serial_request_raw_frame = None
        self.__serial_response_raw_frame = None
        self.__socket_request_frame = None
        self.__socket_response_frame = None
        self.cmd = cmd
        self.data = data

        
    def get_serial_request_raw_frame(self) -> bytes:
        return self.__serial_request_raw_frame
    
    def get_serial_response_raw_frame(self) -> bytes:
        return self.__serial_response_raw_frame

    def get_socket_request_frame(self) -> str:
        return self.__socket_request_frame
    
    def get_socket_response_frame(self) -> str:
        return self.__socket_response_frame

    def set_serial_request_raw_frame(self, data:bytes):
        self.__serial_request_raw_frame = data

    def set_serial_response_raw_frame(self, data:bytes):
        self.__serial_response_raw_frame = data

    def set_socket_request_frame(self, data:str):
        self.__socket_request_frame = data

    def set_socket_response_frame(self, data:str):
        self.__socket_response_frame = data

    def get_serial_request_raw_frame(self) -> bytes:
        return self.__serial_request_raw_frame
    
    def get_socket_response_frame(self) -> str:
        return self.__socket_response_frame

    def set_frame_type(self, type):
        self.cmd = type

    @abstractmethod
    def create_from_Iframe(obj):
        """
           Create frame from Iframe object
        """
        raise NotImplementedError

    class Errors:
        FRAME_ERROR = "Frame error"
        CRC_ERROR = "crc error"

    class Frame_types:
        RAW             = "RAW"
        ERROR           = "ERR"
        SERIAL_CONNECT  = "SRC"
        SERIAL_SEARCH   = "SRS"
        MODBUS_SEARCH   = "MBS" 

class SerialConnectReq(Iframe):

    """
        Perform request for connection or reconection to Serial port                     \n
        Request                                                                          \n
        '{ "cmd": "SRC", "data": { "port_name": "[name]", "port_speed": [bauderate] } }' \n
         Response                                                                        \n
        '{ "cmd": "SRC", "data": { "result" : [bool] } }                                 \n

        additional fields:                                                              \n
        port_name                                                                       \n
        port_speed                                                                      \n
        res                                                                             \n
    """
    
    err_mes = "SerialConnectReq frame error"


    frame:dict =  {"cmd": Iframe.Frame_types.SERIAL_CONNECT, "data": {"port_name": "None", "port_speed": 0, "result": False}}
        
  
    def create_from_Iframe(obj:Iframe):
        if obj is None: return ErrorFrame(SerialConnectReq.err_mes) 
        try:
            port_name = obj.data['port_name']
            port_speed = obj.data['port_speed']
        except KeyError:
            return ErrorFrame(SerialConnectReq.err_mes) 
        except ValueError:
            return ErrorFrame(SerialConnectReq.err_mes) 
        try:
            result  = obj.data['result']
        except KeyError:
            result = False
        except ValueError:
            result = False
        res = SerialConnectReq(port_name, port_speed, result)
        return res
        

    def __init__(self, port_name:str=None, port_speed:int=None, result=False):
        self.port_name = port_name
        self.port_speed = port_speed
        self.result = result
        self.frame["data"]["port_name"]  = port_name
        self.frame["data"]["port_speed"] = port_speed
        req = json.dumps(self.frame)
        self.set_socket_request_frame(req)
        

    @abstractmethod
    def load_response_from_socket(self, frame: str) :
        self.set_serial_response_raw_frame(None)
        self.set_socket_response_frame(None)
        obj = Builder.build_frame(frame)
        if type(obj) is SerialConnectReq:
            self.set_socket_response_frame(frame)
            self.result = obj.result

    def load_response_from_serial(self, result = False):
        self.frame['data']['result'] = result
        self.set_socket_response_frame(json.dumps(self.frame))
        return self.get_socket_response_frame()
        
class ErrorFrame(Iframe):

    def __init__(self, mes: str):
        self.set_frame_type(Iframe.Frame_types.ERROR)
        self.set_socket_response_frame(Iframe.Errors.FRAME_ERROR)
        self.set_socket_request_frame(Iframe.Errors.FRAME_ERROR)
        self.set_serial_request_raw_frame([0])
        self.set_serial_response_raw_frame([0])

    def load_response_from_serial(self, data) -> str:
            return "Can't send error frame"

    #  def load_response_from_serial(self, data:bytes) -> str:
        

class RawFameReq(Iframe):
    """
    Perform request with RAW serial data        \n
    Request                                     \n
    '{ "cmd": "RAW", "data": [1, 20, 0, 47] }'  \n
     Response                                   \n
    '{ "cmd": "RAW", "data": [1, 20, 0, 47] }'  \n
    """
   
    def create_from_Iframe(obj:Iframe):
        if obj is None: return None
        return RawFameReq(obj.data)

    def __init__(self, data:list):
        super().__init__()
        self.set_frame_type(Iframe.Frame_types.RAW)
        crc = util.check_CRC_frame(data)
        if crc :
            self.set_serial_request_raw_frame(bytes(data))
            self.set_socket_request_frame('{"cmd": "RAW" , "data": ' +  str(list((data)))  + ' }')

    def load_response_from_serial(self, data:bytes) -> str:
        crc = util.check_CRC_frame(data)
        if not crc or  data is None:
            self.set_serial_response_raw_frame(None)
            self.set_socket_response_frame(None)
        else:
            self.set_serial_response_raw_frame(bytes(data))
            self.set_socket_response_frame('{"cmd": "RAW" , "data" : ' +  str(list((data)))  + ' }')
            return self.get_socket_response_frame()
        
    def load_response_from_socket(self, frame:str):
        self.set_serial_response_raw_frame(None)
        self.set_socket_response_frame(None)
        obj = Iframe.read(frame)
        self.set_serial_response_raw_frame(bytes(obj.data))
        self.set_socket_response_frame(frame)
     

if __name__ == "__main__":

    # Test Raw request
    print("Test Raw request")
    # create client request
    client = Builder.build_raw_request_with_crc([1, 3, 0, 0, 0, 5])
    # send string line to socket
    socket = client.load_request_to_socket()
    print("1: "+ socket)
    # create server request
    server = Builder.build_frame(socket)
    frame = server.get_socket_request_frame()
    print("2: "+ str(frame))
    # load serial response 
    server.load_response_from_serial(bytes([1, 3, 0, 0, 0, 5, 133, 201]))
    # send string line to socket
    socket = server.get_socket_response_frame()
    # read response on client
    client.load_response_from_socket(socket)
    print("3: "+ str(client.get_serial_response_raw_frame()))

    # Test Serial connect request
    print("Test Serial connect request")
    # create client request
    client = Builder.build_serialconnect_req("COM5", 115200)
    # send string line to socket
    socket = client.load_request_to_socket()
    print("1: "+ socket)
    # create server request
    server = Builder.build_frame(socket)
    frame = server.get_socket_request_frame()
    print("2: "+ str(frame))
    # load serial response 
    server.load_response_from_serial(True)
    # send string line to socket
    socket = server.get_socket_response_frame()
    print("3: " + socket)
    # read response on client
    client.load_response_from_socket(socket)
    print("4: "+ str(client.result))


    


              
    