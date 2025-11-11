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

with open(f"My_scripts2/client_inputs/{client_id}_client") as f:
    input_list = [int(x) for x in f.read().split()]

client = Client(['localhost'] * NUM_SERVERS, PORT_NUM, client_id)

finished = 1 if client_id == NUM_CLIENTS - 1 else 0

for socket in client.sockets:
    os = octetStream()
    os.store(finished)
    os.Send(socket)

def run(input_list):
    print(f"[Client {client_id}] Sending input to servers...")
    client.send_private_inputs(input_list)
    print(f"[Client {client_id}] Done.")

run(input_list)