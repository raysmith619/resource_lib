# wx_rpc_server.py      05Sep2024   crs, from rpc_server.py

def add(a, b):
    return a+b

def sub(a, b):
    return a-b

from wx_rpc import RPCServer
port_host = 50010
server = RPCServer('0.0.0.0',port_host)

server.registerMethod(add)
server.registerMethod(sub)

server.run()