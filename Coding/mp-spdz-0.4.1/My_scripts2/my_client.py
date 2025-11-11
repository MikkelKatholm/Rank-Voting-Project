#!/usr/bin/env python3
"""
client_sum.py
Connects to the MP-SPDZ servers and sends a single input value.
Receives the total sum computed by the MPC parties.
"""
import sys

sys.path.append('../')

from ExternalIO.client import *
from ExternalIO.domains import *
from My_scripts2.consts import *  

from Compiler.library import *

client_id = int(sys.argv[1])

# Read a file on the form
# 0 1 2
# 3 4 5
# ...
#outputting a list of integers i.e [0,1,2,3,4,5,...]
with open(f"My_scripts2/client_inputs/{client_id}_client") as f:
    client_input = [int(x) for x in " ".join(f.readlines()).split()]

input_list = [sint(x) for x in client_input]

client = Client(['localhost'] * NUM_SERVERS, PORT_NUM, client_id)

finished = 1 if client_id == NUM_CLIENTS - 1 else 0

for socket in client.sockets:
    os = octetStream()
    os.store(finished)
    os.Send(socket)

def run(input_list):
    client.send_private_inputs(input_list)

run(input_list)