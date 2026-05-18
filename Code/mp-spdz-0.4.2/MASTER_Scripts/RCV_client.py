import sys, os
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(sys.argv[0]) + "/..")
sys.path.append("ExternalIO/.")
from client import *                                            # type: ignore
from domains import *                                           # type: ignore

script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, "consts.env"))

client_id = int(sys.argv[1])
n_parties = int(os.getenv("NUM_SERVERS"))
PORTNUM = int(os.getenv("PORTNUM"))
ballot_folder = os.getenv("BALLOT_FOLDER")
finish = int(sys.argv[2])

def read_ballot_from_file(client_id):
    filename = os.path.join(ballot_folder, f"{client_id}_ballot.txt")
    ballot = []
    with open(filename, 'r') as f:
        for line in f:
            ballot.extend(map(int, line.split()))
    return ballot

ballot_values = read_ballot_from_file(client_id)

client = Client(['localhost'] * n_parties, PORTNUM, client_id)      # type: ignore
for socket in client.sockets:
    os = octetStream()                                              # type: ignore
    os.store(finish)
    os.Send(socket)

def run(ballot_values):
    client.send_private_inputs(ballot_values)

# running one round for sint

run(ballot_values)
