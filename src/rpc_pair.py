# rpc_pair.py   03Sep2024  crs, From rpc_server.py
""" 
Simple test / exercise of bidirectional use of
remote-procedure-call
"""
import os
import sys
import threading as th
import time

from wx_rpc import RPCServer
from wx_rpc import RPCClient

user_set = False            # User accepting requests
port_host = 50010           # Default listening
if len(sys.argv) > 1:
    port_host = int(sys.argv[1])
port_user = port_host + 10

def pgm_exit(exit_code=0):
    print("pgm_exit")
    running = False
    os._exit(exit_code)
    
def ask(ques):
    print(f"HOST:{ques}")
    return f"What's {ques}"

user_connection = None              # Set to connection to user and recieve requests
def set_user(port=None):
    """ Setup to server user
    :port: user's port
            default: port_user
    """
    global port_user
    global user_connection
    
    if port is None:
        port = port_user
    print(f"set_user({port})")
    port_user = port
    user_connection = RPCClient('localhost', port_user)
    user_connection.connect()
    print(f"set_user({port_user})")

    


host_server = RPCServer(host='localhost', port=port_host)
host_server.registerMethod(pgm_exit)
host_server.registerMethod(set_user)
host_server.registerMethod(ask)
def cmd_in_th_proc():
    host_server.run()

th.Thread(target=cmd_in_th_proc).start()

running = True
def terminal_proc():
    global running
    
    while running:
        inp = input("type cmd:")
        print(f"input:{inp}")
        cmds = inp.split()
        cmd = cmds[0].lower() if len(cmds) > 0 else None
        cmd_arg = cmds[1] if len(cmds) > 1 else None
        cmd_args = cmds[1:] if len(cmds) >  0 else []
        if cmd == 'user_cmd':
            user_connection.user_cmd(cmd_args)
        elif cmd == 'user_disconnect':
            user_connection.disconnect()
        elif cmd == "exit":
            user_connection.pgm_exit()
            pgm_exit()
        else:
            print(f"Don't understand {cmd}")
            
th.Thread(target=terminal_proc).start()

while running:
    time.sleep(1)
    