# rpc_ask.py
import os
import sys
import threading as th
import time
from wx_rpc import RPCClient
from wx_rpc import RPCServer

if len(sys.argv) > 1:
    ques = sys.argv[1]
port_host = 50010           # Default listening
if len(sys.argv) > 2:
    port_host = int(sys.argv[2])
port_user = port_host + 10

host_server = RPCClient('localhost', port_host)
host_server.connect()

running = True

def user_cmd(*args):
    """ command request of user
    :args: arguments
    """
    print(f"USER: args:{args}")

def pgm_exit(exit_code=0):
    global running
    running = False
    print("pgm_exit")
    os._exit(exit_code)
    
        
def host_req_setup():
    """ Setup server to handling requests from host
    """
    user_server = RPCServer(host='localhost', port=port_user)
    user_server.registerMethod(user_cmd)
    user_server.registerMethod(pgm_exit)
    def cmd_in_th_proc():
        user_server.run()

    th.Thread(target=cmd_in_th_proc).start()

def terminal_proc():
    while running:
        inp = input("type cmd:")
        print(f"input:{inp}")
        cmds = inp.split()
        cmd = cmds[0].lower() if len(cmds) > 0 else None
        cmd_arg = cmds[1] if len(cmds) > 1 else None
        cmd_args = cmds[1:] if len(cmds) >  0 else []
        if cmd == 'set_user':
            host_req_setup()    # Setup server to handle requests from host
            print(f"host_server.set_user({port_user})")
            host_server.set_user(port_user)
        elif cmd == 'ask':
            host_server.ask(cmd_args)
        elif cmd == 'exit':
            host_server.pgm_exit()
            pgm_exit()
        else:
            print(f"Don't know {cmd} - {inp}")    
th.Thread(target=terminal_proc).start()

while running:
    time.sleep(1)
    
host_server.disconnect()