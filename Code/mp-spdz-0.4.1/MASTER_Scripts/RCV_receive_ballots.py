from Compiler.types import *
from Compiler.GC.types import *
from Compiler.library import *
from Compiler.util import if_else

from MASTER_Scripts.consts import *

BALLOT_SIZE = NUM_CANDS

def accept_client():
    client_socket_id = accept_client_connection(PORTNUM)
    last = regint.read_from_socket(client_socket_id)
    return client_socket_id, last

def close_all_connections(number_clients):
    @for_range(number_clients)
    def _(i):
        closeclientconnection(i)

def client_input(client_socket_id) -> list[sint]:
    """
    Send share of random value, receive input and deduce share.
    """
    return sint.receive_from_client(BALLOT_SIZE, client_socket_id)

def debug_print(secret_ballot):
    if not DEBUG:
        return
    for elem in secret_ballot:
        clear_val = elem.reveal()
        print_ln('%s', clear_val)

def run_client_server() -> Matrix: 
    listen_for_clients(PORTNUM)
    print_ln("👂 Listening for client connections on base port %s", PORTNUM)

    client_sockets = Array(NUM_CLIENTS, regint)
    number_clients =  MemValue(regint(0))
    seen = Array(NUM_CLIENTS, regint)
    seen.assign_all(0)

    # Use a Matrix to store all ballots.
    # Rows = clients, Cols = flattened ballot entries
    flat_ballots = Matrix(BALLOT_SIZE, NUM_CLIENTS, sint)
    flat_ballots.assign_all(-1)

    @do_while
    def _():
        client_id, last = accept_client()
        client_sockets[client_id] = client_id
        seen[client_id] = 1
        @if_(last == 1)
        def _():
            number_clients.write(client_id + 1)
        return (sum(seen) < number_clients) + (number_clients == 0)
    
    @for_range(number_clients)
    def _(client_id):
        ballot_sint = client_input(client_id)
        for i in range(BALLOT_SIZE):
            flat_ballots[i][client_id] = ballot_sint[i]
        debug_print(ballot_sint)
        closeclientconnection(client_id)
    return flat_ballots

def format_ballots_as_list(flat_ballots: Matrix) -> list[Array]:
    ballots: list[Array] = []
    for idx in range(NUM_CLIENTS):        
        ballot_array = Array(length=BALLOT_SIZE, value_type=sint)
        flat_ballot = flat_ballots.get_column(idx)
        for i in range(BALLOT_SIZE):
            ballot_array[i] = flat_ballot[i]
        ballots.append(ballot_array)
    return ballots

def receive_ballots():
    flat_ballots = run_client_server()
    ballots = format_ballots_as_list(flat_ballots)
    return ballots
