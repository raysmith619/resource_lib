# dots_shadow_timeit.py
""" Do timing on DotsShadow / MoveList
vs simpler implementations.
"""
import timeit
import random
import numpy as np

from dots_shadow import DotsShadow, MoveList
from docutils.nodes import row

# test numpy array against list
rn = 1000000
###rn = 1000
nlen = 50
def test1(rn=1000000, nlen=50):
    global l1
    l1 = []
    for i in range(nlen):
        nv = random.randint(1,nlen)
        l1.append(nv)
    global npl1
    npl1 = np.zeros([nlen], dtype=int)
    for i in range(nlen):
        npl1[i] = l1[i]

    print()
    print("nlen={:d} timeit count={:d}".format(nlen, rn))
    print("indexed access")
    print( "= l1[]: ", timeit.timeit("for n in range(nlen): x |= l1[n]", setup='x=0', number=rn, globals=globals()))
    print( "= np.l1[]: ", timeit.timeit("for n in range(nlen): x |= npl1[n]", setup='x=0', number=rn, globals=globals()))
    
    print("append l2[]: ", timeit.timeit("for n in range(nlen): l2.append(1)", setup="l2=[]", number=rn, globals=globals()))
    print("nlp[]=: ", timeit.timeit("for i in range(nlen): npl[i]=1", setup="npl=np.zeros([nlen],dtype=int)", number=rn, globals=globals()))
    
    class et:
        def __init__(self, row, col, hv):
            self.row=row
            self.col=col
            self.hv = hv
    global etlist
    etlist = []
    for i in range(nlen):
        etlist.append(et(i+1,i+2, i%2))
    
    global etalist
    etalist = [[0 for i in range(3)] for j in range(nlen)]
    for i in range(nlen):
        etalist[i] [0] = etlist[i].row
        etalist[i] [1] = etlist[i].col
        etalist[i] [2] = etlist[i].hv
    
    global np_etlist    
    np_etlist = np.zeros([nlen, 3], dtype=int)
    for i in range(nlen):
        np_etlist[i, 0] = etlist[i].row
        np_etlist[i, 1] = etlist[i].col
        np_etlist[i, 2] = etlist[i].hv
    
    print("etlist: = l[i].col", timeit.timeit("for i in range(nlen): x |= etlist[i].col", setup="x=0", number=rn, globals=globals()))
    print("etalist = l[i,1]", timeit.timeit("for i in range(nlen): x |= etalist[i][1]", setup="x=0", number=rn, globals=globals()))
    print("np_etlist = l[i,1]", timeit.timeit("for i in range(nlen): x |= np_etlist[i,1]", setup="x=0", number=rn, globals=globals()))
        

test1(1000, 50)
test1(1000, 500)
test1(1000, 5000)
test1(1000, 50000)
test1(1000, 500000)
test1(1000, 5000000)
test1(1000, 50000000)
