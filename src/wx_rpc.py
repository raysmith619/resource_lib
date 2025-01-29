# wx_rpc.py 30Aug2024  crs  from examples/rpc.py 
# rpc.py    27Aug2024  from https://github.com/TarasZhere/RPC

import json
import socket
import inspect
import traceback
from threading import Thread
from select_trace import SlTrace
SIZE = 2**16


class RPCServer:

    def __init__(self, host:str='0.0.0.0', port:int=8080) -> None:
        self.host = host
        self.port = port
        self.address = (host, port)
        self._methods = {}

    def help(self) -> None:
        SlTrace.lg('REGISTERED METHODS:')
        for method in self._methods.items():
            SlTrace.lg('\t',method)

    '''

        registerFunction: pass a method to register all its methods and attributes so they can be used by the client via rpcs
            Arguments:
            instance -> a class object
    '''
    def registerMethod(self, function) -> None:
        try:
            self._methods.update({function.__name__ : function})
        except:
            raise Exception('A non method object has been passed into RPCServer.registerMethod(self, function)')

    '''
        registerInstance: pass a instance of a class to register all its methods and attributes so they can be used by the client via rpcs
            Arguments:
            instance -> a class object
    '''
    def registerInstance(self, instance=None) -> None:
        try:
            # Regestring the instance's methods
            for functionName, function in inspect.getmembers(instance, predicate=inspect.ismethod):
                if not functionName.startswith('__'):
                    self._methods.update({functionName: function})
        except:
            raise Exception('A non class object has been passed into RPCServer.registerInstance(self, instance)')

    '''
        handle: pass client connection and it's address to perform requests between client and server (recorded fucntions or) 
        Arguments:
        client -> 
    '''
    def __handle__(self, client:socket.socket, address:tuple):
        SlTrace.lg(f'Managing requests from {address}.', "rpc")
        while True:
            try:
                functionName, args, kwargs = json.loads(client.recv(SIZE).decode())
            except: 
                SlTrace.lg(f'! Client {address} disconnected.')
                break
            # Showing request Type
            SlTrace.lg(f'> {address} : {functionName}({args})', "rpc")
            
            try:
                response = self._methods[functionName](*args, **kwargs)
            except Exception as e:
                estr = "Exception:" + str(e)
                tbstk = traceback.extract_stack()
                tbstk_lst = traceback.format_list(tbstk)
                tbstr = "\n".join(tbstk_lst)
                SlTrace.lg(f"RPCServer Exception: {estr}")
                SlTrace.lg(f"__handle__({functionName}, {args}, {kwargs})")
                SlTrace.lg(f"{tbstr}\n")
                # Send back exeption if function called by client is not registred 
                client.sendall(json.dumps(estr).encode())
            else:
                client.sendall(json.dumps(response).encode())


        SlTrace.lg(f'Completed request from {address}.')
        client.close()
    
    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(self.address)
            sock.listen()

            SlTrace.lg(f'+ Server {self.address} running', "rpc")
            while True:
                try:
                    client, address = sock.accept()

                    Thread(target=self.__handle__, args=[client, address]).start()

                except KeyboardInterrupt:
                    SlTrace.lg(f'- Server {self.address} interrupted')
                    break



class RPCClient:
    def __init__(self, host:str='localhost', port:int=8080) -> None:
        self.__sock = None
        self.__address = (host, port)


    def isConnected(self):
        try:
            self.__sock.sendall(b'test')
            self.__sock.recv(SIZE)
            return True

        except:
            return False


    def connect(self):
        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            SlTrace.lg(f"connect({self.__address})", "rpc")
            self.__sock.connect(self.__address)
        except EOFError as e:
            SlTrace.lg(e)
            SlTrace.lg(f"connect({self.__address})")
            raise Exception('Client was not able to connect.')
    
    def disconnect(self):
        try:
            self.__sock.close()
        except:
            pass


    def __getattr__(self, __name: str):
        def excecute(*args, **kwargs):
            self.__sock.sendall(json.dumps((__name, args, kwargs)).encode())

            response = json.loads(self.__sock.recv(SIZE).decode())
   
            return response
        
        return excecute

    def __del__(self):
        try:
            self.__sock.close()
        except:
            pass