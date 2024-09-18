# wx_rpc_client.py      05Sep2024  crs, from rpc_client.property
 
from wx_rpc import RPCClient
port_host = 50010
server = RPCClient('localhost', port_host)

server.connect()

print(server.add(5, 6))
print(server.sub(5, 6))

server.disconnect()