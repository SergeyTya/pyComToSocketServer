import time
from pyModbusTCP.client import ModbusClient


def main():
    print("start")
    c = ModbusClient(host='localhost', port=8888 )
    c.open()

    
    c._sock.send("close".encode())
    print(c._sock.recv(256))



if __name__ == "__main__":
    main()