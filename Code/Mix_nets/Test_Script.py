import subprocess

def write_consts_to_file(consts, filename="Consts_script.py"):
    with open("Consts_script.py", "w") as f:
        for key, value in consts.items():
            f.write(f"{key} = {value}\n")

def main():

    servers_default = 5
    clients_default = 1_0
    candidates_default = 5

    servers = [i for i in range(2,11)]
    clients = [2**i for i in range(2,21)]
    candidates = [2*i for i in range(2,11)]

    consts = dict(
        NUM_SERVERS = 0,
        NUM_CLIENTS = 0,
        NUM_CANDS = 0,
        THRESHOLD = 0
    )

    for num_servers in servers:
        print(f"Running protocol with {num_servers} servers, {clients_default} clients and {candidates_default} candidates...")
        setup_and_run_protocol(consts, num_servers, clients_default, candidates_default)
    
    for num_clients in clients:
        print(f"Running protocol with {servers_default} servers, {num_clients} clients and {candidates_default} candidates...")
        setup_and_run_protocol(consts, servers_default, num_clients, candidates_default)
    
    for num_cands in candidates:
        print(f"Running protocol with {servers_default} servers, {clients_default} clients and {num_cands} candidates...")
        setup_and_run_protocol(consts, servers_default, clients_default, num_cands)


def setup_and_run_protocol(consts, num_servers, num_clients, num_cands):
        consts['NUM_SERVERS'] = num_servers
        consts['NUM_CLIENTS'] = num_clients
        consts['NUM_CANDS'] = num_cands
        threshold = num_servers // 2 + 1
        if threshold > num_servers:
            threshold = num_servers
        consts['THRESHOLD'] = threshold 

        write_consts_to_file(consts)
        subprocess.run(["python3", "run.py"])



if __name__ == "__main__":
    main()