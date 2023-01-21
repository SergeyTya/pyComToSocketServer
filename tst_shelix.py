import shlex

mes = "type RAW"

class Client_type:
    MODBUS   = "modbus"
    RAW      = "raw"
    LISTENER = "listener"
    DEFAULT  = ""
    
def parse(mes):
    res= shlex.split(mes)
    res = list(res)
    try:
        if 'type' in res:
            tp = res[res.index('type')+1]
            print(tp)
            if tp is Client_type.LISTENER: return Client_type.LISTENER
            if tp is Client_type.RAW:      return Client_type.RAW
            if tp is Client_type.MODBUS:   return Client_type.MODBUS
            return Client_type.DEFAULT
    except IndexError: pass


print( parse(mes) )

