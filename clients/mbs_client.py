from pyModbusTCP.client import ModbusClient
import time
import sys


def main():
    print("start")
    c = ModbusClient(host='localhost', port=8888 )
    c.open()

    c._sock.send(" type modbus ".encode())
    print(c._sock.recv(256))

    rr = c.custom_request(bytes([28 , 0,2 , 0,3 , 0,0 , 0,0 ]))
    rr = c.custom_request(bytes([0x19 , 1, 0]))
    #rr = c.custom_request(bytes([0x14]))

    while(True):
        #rr = c.read_input_registers(0, 10)
        rr = c.custom_request(bytes([27 , 0, 1]))
        print(str(time.time()) + "  "+ str(rr))
        print("len=", len(rr))
        time.sleep(1)
    # rr = c.read_input_registers(0, 10)
    # print(str(time.time()) + str(rr))
    # c._sock.send(" type listener ".encode())
    # while True:
    #     res =c._sock.recv(256)
    #     print(res)

if __name__ == "__main__":
    main()