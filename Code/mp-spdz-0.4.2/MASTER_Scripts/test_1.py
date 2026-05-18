from Compiler.types import *
from Compiler.GC.types import *
from Compiler.library import *
from Compiler.util import if_else



def run_test():
    a = Array(10, sint)
    a.assign_all(0)
    for i in range(len(a)):
        print_ln("a[%s] = %s", i, a[i].reveal())
    print_ln("Done")

