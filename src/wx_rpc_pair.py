# wx_rpc_pair.py   03Sep2024  crs, From rpc_pair.py
""" 
Setup bidirectional RPC connection
"""
import os
import sys
import threading as th
import time
import socket

from wx_rpc import RPCServer
from wx_rpc import RPCClient

from select_trace import SlTrace

class G_RPCClient(RPCClient):
    """ Guarded client, with check
    """
    def __init__(self, rpc_pair, **kwargs):
        self.rpc_pair = rpc_pair
        self.is_connected = False
        super().__init__(**kwargs)
        SlTrace.lg("G_RPCClient initialized")


    def __getattr__(self, __name: str):
        self.wait_connected()
        return super().__getattr(__name)

    
    def check_connected(self):
        """ Check if remote ready, connects if possible
        :returns: True iff remote ready to accept request(function call)
        """
        if not self.is_connected:
            try: 
                self.connecton_remote.connect()
                self.is_connected_remote = True
            except:
                return False
        return True

    def wait_connected(self):
        """ Wait for remote connection, tries to connect
        """
        SlTrace.lg("wait_connection")
        while not self.check_connected():
            time.sleep(.1)    
        SlTrace.lg("connection achieved")
        
class RPCPair():
    """ Bidirectional RPC connection
        server_local - services requests from remote
        connection_remote - makes requests of remote server
                delays requests untill remote server is connected
    """
    PORT_LOCAL = 50010
    PORT_REMOTE = PORT_LOCAL+20
    
    def __init__(self, host_local=None, port_local=None):
        """ Setup local server
        :host_local: local host name default: our host name
        :port_local: local port number default: 50010
        """
        if host_local is None:
            host_local = socket.gethostname()
        self.host_local = host_local
        if port_local is None:
            port_local = RPCPair.PORT_LOCAL
        self.port_local = port_local
        self.local_server = RPCServer(self.host_local, self.port_local)
        self.connection_remote = None       # Set when/if ready

        def local_server_proc():
            self.local_server.run()
        th.Thread(target=local_server_proc).start()

        self.registerMethod(self.setup_calls_to_user)
        

    def setup_calls_to_user(self, host_remote=None, port_remote=None):
        """ Setup for calls to user
        :host_remote: remote host name default: our hostname
        :port_remote: remote port number
        """
        if host_remote is None:
            host_remote = self.host_remote
        self.host_reme = host
        if port_remote is None:
            port_remote = RPCPair.PORT_REMOTE        
        self.port_remote = port_remote
        
        self.connection_remote = RPCClient(self, host=self.host_remote,
                                             port=self.port_remote)
        
    def registerMethod(self, method):
        """ Register local function with server
        :method: local function to be run
        """
        self.local_server.registerMethod(method)

    
if __name__ == '__main__':
    # Usage: wx_rpc_pair.py [host|user|-] [port_local] [port_remote]
    host_or_user = "host"
    host_local = None
    host_remote = None
    port_local = RPCPair.PORT_LOCAL
    port_remote = None
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg != "-":
            host_or_user = arg
    if len(sys.argv) > 2 and sys.argv[2] != '-':
        port_local = sys.argv[2]
    if len(sys.argv) > 3 and sys.argv[3] != '-':
        port_remote = sys.argv[3]
        
    def echo(msg):
        """ echo message locally
        :msg: message to echo
        :returns: msg - echo
        """
        SlTrace.lg(msg)
        return f"{msg} - echo"
    
    SlTrace.lg(f"\n{os.path.basename(__file__)} Self Test")
    
    if host_or_user == "user":
        temp = port_local       # Switch local and remote
        port_local = port_remote
        port_remote = temp
        temp = host_local       # Switch local and remote
        host_local = host_remote
        host_remote = temp
            
    msg = "foo"
    SlTrace.lg(f"""
    rp = RPCPair(host_local={host_local}, port_local={port_local})
               """)
    rp = RPCPair(host_local=host_local, port_local=port_local)
    
    running = True
    if host_or_user == "user":
        SlTrace.lg(f"USER:{host_or_user}")
        for n in range(1,10+1):
            SlTrace.lg(f"{n}:")
            val = rp.connection_remote.echo(msg)
            SlTrace.lg(f"ret: {n}: {val}")
            
    else:
        SlTrace.lg(f"Host: {host_or_user}")
        rp.registerMethod(echo)
        SlTrace.lg(f"{host_or_user} registered {echo}")
        host_msg = f"from host {msg}"
        SlTrace.lg(f"""
        resp = rp.connection_remote.echo({host_msg})
        """)
        resp = rp.connection_remote.echo(host_msg)
        SlTrace.lg(f"resp to {msg}: {resp}")
        while running:
            time.sleep(.1)
    SlTrace.lg(f"Test End: {host_or_user}")            
    