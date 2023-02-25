import os
import tkinter as tk
import tkinter.font as tkFont

class App:
    def __init__(self, root):
        #setting title
        root.title("CTS launcher")
        #setting window size
        main_width=400
        main_height=180

        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (main_width, main_height, (screenwidth - main_width) / 2, (screenheight - main_height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        self.GLineEdit_log=tk.Text(root)
        self.GLineEdit_log["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.GLineEdit_log["font"] = ft
        self.GLineEdit_log["fg"] = "#333333"
        self.GLineEdit_log.place(x=main_width*0.48,y=5,width=main_width*0.5,height=main_height-10)

        GLabel_12=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_12["font"] = ft
        GLabel_12["fg"] = "#333333"
        GLabel_12["justify"] = "center"
        GLabel_12["text"] = "Server:"
        GLabel_12.place(x=20,y=5,width=70,height=25)

        GLabel_765=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_765["font"] = ft
        GLabel_765["fg"] = "#333333"
        GLabel_765["justify"] = "center"
        GLabel_765["text"] = "Port:"
        GLabel_765.place(x=20,y=35,width=70,height=25)

        GLabel_885=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_885["font"] = ft
        GLabel_885["fg"] = "#333333"
        GLabel_885["justify"] = "center"
        GLabel_885["text"] = "Com name:"
        GLabel_885.place(x=20,y=65,width=70,height=25)

        GLabel_319=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_319["font"] = ft
        GLabel_319["fg"] = "#333333"
        GLabel_319["justify"] = "center"
        GLabel_319["text"] = "Com speed:"
        GLabel_319.place(x=20,y=95,width=70,height=25)

        self.GButton_Run=tk.Button(root)
        self.GButton_Run["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        self.GButton_Run["font"] = ft
        self.GButton_Run["fg"] = "#000000"
        self.GButton_Run["justify"] = "center"
        self.GButton_Run["text"] = "Run"
        self.GButton_Run.place(x=10,y=150,width=70,height=25)
        # self.GButton_Run["command"] = self.GButton_560_command

        self.GButton_Close=tk.Button(root)
        self.GButton_Close["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        self.GButton_Close["font"] = ft
        self.GButton_Close["fg"] = "#000000"
        self.GButton_Close["justify"] = "center"
        self.GButton_Close["text"] = "Close"
        self.GButton_Close.place(x=100,y=150,width=70,height=25)
        # self.GButton_Close["command"] = (lambda : os._exit(-1))
        self.GButton_Close["command"] = (lambda : root.destroy())


        self.Edit_Socket_name=tk.Entry(master=root)
        self.Edit_Socket_name["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.Edit_Socket_name["font"] = ft
        self.Edit_Socket_name["fg"] = "#333333"
        self.Edit_Socket_name["justify"] = "center"
        self.Edit_Socket_name.place(x=100,y=5,width=77,height=30)

        self.Edit_socket_port=tk.Entry(master=root)
        self.Edit_socket_port["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.Edit_socket_port["font"] = ft
        self.Edit_socket_port["fg"] = "#333333"
        self.Edit_socket_port["justify"] = "center"
        self.Edit_socket_port.place(x=100,y=35,width=77,height=30)

        self.Edit_serial_name=tk.Entry(master=root)
        self.Edit_serial_name["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.Edit_serial_name["font"] = ft
        self.Edit_serial_name["fg"] = "#333333"
        self.Edit_serial_name["justify"] = "center"
        self.Edit_serial_name.place(x=100,y=65,width=77,height=30)

        self.Edit_serial_speed=tk.Entry(master=root)
        self.Edit_serial_speed["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.Edit_serial_speed["font"] = ft
        self.Edit_serial_speed["fg"] = "#333333"
        self.Edit_serial_speed["justify"] = "center"
        self.Edit_serial_speed.place(x=100,y=95,width=77,height=30)

    def set_Edits(self, socket_name:str, socket_port:int, serial_name:str, serial_speed:int):
        self.Edit_serial_name.insert(0,serial_name)
        self.Edit_serial_speed.insert(0,serial_speed)
        self.Edit_socket_port.insert(0,socket_port)
        self.Edit_Socket_name.insert(0,socket_name)

    def get_serial_name(self):
        return self.Edit_serial_name.get()
    
    def get_serial_speed(self):
        return self.Edit_serial_speed.get()
    
    def get_socket_name(self):
        return self.Edit_Socket_name.get()
    
    def get_socket_port(self):
        return self.Edit_socket_port.get()
    
    def write_log(self, mes:str):
        self.GLineEdit_log.insert("end",mes+"\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
