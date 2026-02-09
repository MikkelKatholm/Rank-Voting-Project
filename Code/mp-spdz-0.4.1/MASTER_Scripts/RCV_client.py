#!/usr/bin/python3

import sys, os

sys.path.insert(0, os.path.dirname(sys.argv[0]) + "/..")
sys.path.append("ExternalIO/.")

from client import *
from domains import *

client_id = int(sys.argv[1])
n_parties = int(sys.argv[2])
client_ballot = [1, 0, 0, 1]
finish = int(sys.argv[3])

client = Client(['localhost'] * n_parties, 14000, client_id)

for socket in client.sockets:
    os = octetStream()
    os.store(finish)
    os.Send(socket)

def run(x):
    client.send_private_inputs([x])
    print("Ballot sent")

    print('Winning client id is :', client.receive_outputs(1)[0])

# running two rounds
# first for sint, then for sfix
run(client_ballot)
