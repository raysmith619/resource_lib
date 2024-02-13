#mp1.py 04Feb2024   crs, From stackoverflow

from multiprocessing import Process,Pipe

def f(child_conn):
    msg = "Hello"
    child_conn.send(msg)
    child_conn.send(" There")
    child_conn.close()