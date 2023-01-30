import time
from pyModbusTCP.client import ModbusClient


def main():
    print("start")
    c = ModbusClient(host='localhost', port=8888 )
    c.open()

    while(True):
        c._sock.send(" info ".encode())
        print(c._sock.recv(256))
        time.sleep(1)


if __name__ == "__main__":
    main()