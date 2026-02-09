#!/usr/bin/python3

import sys, os

sys.path.insert(0, os.path.dirname(sys.argv[0]) + "/..")
sys.path.append("ExternalIO/.")

from client import *
from domains import *

client_id = int(sys.argv[1])
n_parties = int(sys.argv[2])
# Ballot is a 2x2 matrix flattened: 4 values for NUM_CANDS * NUM_CANDS
client_ballot = [1, 0, 0, 1]
finish = int(sys.argv[3])

client = Client(['localhost'] * n_parties, 14000, client_id)

for socket in client.sockets:
    os = octetStream()
    os.store(finish)
    os.Send(socket)

def run(ballot_values):
    client.send_private_inputs(ballot_values)
    print("Ballot sent")

    print('Winning candidate is:', client.receive_outputs(1)[0])

# running one round for sint
run(client_ballot)
