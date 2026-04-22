from Compiler.GC.types import sbitintvec, sbits
from Compiler.library import *
from dotenv import load_dotenv
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, "consts.env"))

PORTNUM = int(os.getenv("PORTNUM"))
NUM_CLIENTS = int(os.getenv("NUM_VOTERS"))
NUM_CANDS = int(os.getenv("NUM_CANDS"))
RUN_LEAK_VERSION = bool(int(os.getenv("RUN_LEAK_VERSION")))
n_threads = 4
DEBUG = bool(int(os.getenv("DEBUG")))


SEC_PARAM = 40
# NBITS must be >= GC statistical security parameter to avoid internal XORS range errors
NBITS = max(SEC_PARAM, (NUM_CLIENTS + 1).bit_length())

sb = sbits.get_type(1)


def print_ballot_as_matrix(ballot_matrix: Matrix):
    clear = ballot_matrix.reveal_nested()
    for row in clear:
        print_ln("%s", row)


TIMER_IDS = {
    "send_and_receive_ballots": 10,
    "clean_ballots": 11,
    "convert_ballots": 12,
    "tally": 13,
}


def dict_value_to_key(d: dict, value):
    for k, v in d.items():
        if v == value:
            return k
    raise ValueError(f"Value {value} not found in dictionary")