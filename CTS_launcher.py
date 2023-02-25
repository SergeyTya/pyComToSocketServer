
import asyncio
import os
import tkinter as tk
import tkinter.font as tkFont
import CTS_ln_form
import sys
import serial.tools.list_ports
import json

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from CTS_server import start_server

class CTS_GUI_param:
    def __init__(self):
        try:
            self.read()
        except FileNotFoundError:
            self.setup()
            self.write()
            pass

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    def fromJSON(self, lime:str):
        pass
    
    def write(self):
        with open('data.json', 'w') as f:
            f.write(self.toJSON())
    
    def read(self):
        with open('data.json', 'r') as f:
            d = json.load(f)
            self.socket_name = d['socket_name']
            self.socket_port = d['socket_port']
            self.serial_name = d['serial_name']
            self.serial_speed = d['serial_speed']

    def setup(self,
              socket_name:str="localhost", 
              socket_port:int=8888, 
              serial_name:str="COM1",
              serial_speed:int=9600):
        self.socket_name:str = socket_name
        self.socket_port:int = socket_port
        self.serial_name:str = serial_name
        self.serial_speed:int = serial_speed
        self.write()



class App(tk.Tk):

    def close(self):
        for task in self.tasks:
            task.cancel()
        loop.stop()
        self.destroy()

    async def updater(self, interval):
        while True:
            self.update()
            await asyncio.sleep(interval)
    
    def __init__(self, loop, interval=1/120):
        self.param = CTS_GUI_param()
        super().__init__()
        self.loop = loop
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.tasks = []
        self.main = CTS_ln_form.App(self)
        
        self.main.set_Edits(self.param.socket_name, self.param.socket_port, self.param.serial_name, self.param.serial_speed)
        self.main.GButton_Run["command"] = self.run_server
        serials = serial.tools.list_ports.comports()
        self.main.write_log("Port available: ")
        for port in serials:
            self.main.write_log(port.name)
        if len(serials) == 0:
            self.main.write_log("None")

        self.tasks.append(loop.create_task(self.updater(interval)))

    def run_server(self):
        self.main.write_log("Starting \n")
        self.param.setup(
            self.main.get_socket_name(),
            self.main.get_socket_port(),
            self.main.get_serial_name(),
            self.main.get_serial_speed()
            )
        loop.create_task(
            start_server(
            loop = loop, 
            com_name=self.param.serial_name, 
            com_speed= self.param.serial_speed, 
            ip=self.param.socket_name, 
            port=self.param.socket_port 
        ))

    def get_serials():
        pass

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = App(loop)
    loop.run_forever()
    loop.close()
