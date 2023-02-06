from pyModbusTCP.client import ModbusClient
import time
import sys

def main():
    print("start")
    c = ModbusClient(host='localhost', port=8888 )
    c.open()

    c._sock.send(" type modbus ".encode())
    print(c._sock.recv(256))

    while(True):
        rr = c.read_input_registers(0, 10)
        print(str(time.time()) + "  "+ str(rr))
        time.sleep(1)
    # rr = c.read_input_registers(0, 10)
    # print(str(time.time()) + str(rr))
    # c._sock.send(" type listener ".encode())
    # while True:
    #     res =c._sock.recv(256)
    #     print(res)

if __name__ == "__main__":
    main()