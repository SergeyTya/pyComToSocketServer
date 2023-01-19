from pyModbusTCP.client import ModbusClient
import time
import sys

def main():
    c = ModbusClient(host='localhost', port=8888 )
    c.open()
    while(True):
        rr = c.read_input_registers(0, 10)
        print(str(time.time()) + str(rr))


if __name__ == "__main__":
    main()