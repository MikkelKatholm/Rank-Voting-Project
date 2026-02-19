from Compiler.GC.types import sbitintvec, sbits
from Compiler.library import *
from dotenv import load_dotenv
import os


load_dotenv("consts.env")

PORTNUM = int(os.getenv("PORTNUM"))
NUM_CLIENTS = int(os.getenv("NUM_VOTERS"))
NUM_CANDS = int(os.getenv("NUM_CANDS"))
n_threads = 4
DEBUG = bool(int(os.getenv("DEBUG")))


SEC_PARAM = 40
# NBITS must be >= GC statistical security parameter to avoid internal XORS range errors
NBITS = max(SEC_PARAM, (NUM_CLIENTS + 1).bit_length())
sb = sbits.get_type(NBITS)
siv = sbitintvec.get_type(NBITS)

def print_ballot_as_matrix(ballot_matrix: Matrix):
    clear = ballot_matrix.reveal_nested()
    for row in clear:
        print_ln("%s", row)