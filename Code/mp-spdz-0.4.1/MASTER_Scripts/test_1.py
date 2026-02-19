from Compiler.types import *
from Compiler.GC.types import *
from Compiler.library import *
from Compiler.util import if_else



def run_test():
    @if_e(1 == 1)
    def _():
        print_ln("Test passed!")
    @else_
    def _():        
        print_ln("Test failed!")

