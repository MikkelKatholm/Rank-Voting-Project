import sys
client_id = int(sys.argv[1])

with open(f"My_scripts2/client_inputs/{client_id}_client") as f:
    client_input =[int(x) for x in f.read().split()]

print("Client", client_id, "input:", client_input)