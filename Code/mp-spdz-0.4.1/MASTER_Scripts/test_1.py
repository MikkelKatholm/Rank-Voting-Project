from Compiler.types import *
from Compiler.GC.types import *
from Compiler.library import *
from Compiler.util import if_else



def run_test():
    for i in range(1000):    
        @if_e(1 == 1)
        def _():
            print_str("a")
        @else_
        def _():        
            print_ln("b")
    print_ln("Done")

