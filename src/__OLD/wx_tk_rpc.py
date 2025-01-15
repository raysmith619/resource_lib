# wx_tk_rpc.py 10Oct2024  crs  from wx_rpc.py 
# rpc.py    27Aug2024  from https://github.com/TarasZhere/RPC
# Using tkinter's after to avoid error: main thread is not in main loop
import json
import socket
import inspect
import traceback
from select_trace import SlTrace
SIZE = 2**16


class RPCServer:

    def __init__(self, root, host:str='0.0.0.0', port:int=8080) -> None:
        self.root = root
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
        SlTrace.lg(f'Managing requests from {address}.')
        self.__handle_a__(client, address)
        
    
    def __handle_a__(self, client:socket.socket, address:tuple):
            try:
                functionName, args, kwargs = json.loads(client.recv(SIZE).decode())
                self.do__handle_a__ = True
            except: 
                SlTrace.lg(f'! Client {address} disconnected.')
                self.do__handle_a__ = False
                SlTrace.lg(f'Completed request from {address}.')
                client.close()
                return
            
            # Showing request Type
            SlTrace.lg(f'> {address} : {functionName}({args})')
            
            try:
                response = self._methods[functionName](*args, **kwargs)
                self.do__handle_a__ = True
            except Exception as e:
                self.do__handle_a__ = False
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

            self.root.after(0, self.__handle_a__, client, address)
    
    def run(self) -> None:
        self.run_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.run_sock.bind(self.address)
        self.run_sock.listen()

        SlTrace.lg(f'+ Server {self.address} running')
        self.do_run_a =  True        
        self.run_a()
        
    def run_a(self):
        while self.do_run_a:
            try:
                client, address = self.run_sock.accept()

                self.__handle__(client, address)
            except KeyboardInterrupt:
                SlTrace.lg(f'- Server {self.address} interrupted')
                self.do_run_a = False
            if self.do_run_a:
                self.root.after(0, self.run_a)


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
            SlTrace.lg(f"connect({self.__address})")
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