import run

def write_consts_to_file(consts, filename="Consts_script.py"):
    with open("Consts_script.py", "w") as f:
        for key, value in consts.items():
            f.write(f"{key} = {value}\n")

def main():
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
        for num_clients in clients:
            for num_cands in candidates:
                for threshold in range(1, num_servers):
                    consts['NUM_SERVERS'] = num_servers
                    consts['NUM_CLIENTS'] = num_clients
                    consts['NUM_CANDS'] = num_cands
                    consts['THRESHOLD'] = threshold

                    write_consts_to_file(consts)
                    run.run_all()



if __name__ == "__main__":
    main()