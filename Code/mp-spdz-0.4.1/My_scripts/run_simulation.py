import subprocess
import os
import generate_ballots
import time

c_val="3"
s_val="3"
v_val="32"
f_val="1"
gen_ballots=True

leak = True
protocol = f"rcv_matrix{"_leak" if leak else ""}"

for c_val in range(3, 10):
    print(f"Candidates = {c_val}")
    file_contents= f"NUM_CANDIDATES = {c_val}\nNUM_PARTIES = {s_val}\nNUM_VOTES = {v_val}\nFIELD_SIZE = 2**{f_val}\nNUM_SHARES = NUM_PARTIES\nTHRESHOLD = NUM_PARTIES"
    with open("consts.py", "w") as f:
        f.write(file_contents)

    time.sleep(0.5)
    
    subprocess.run(["python3", "../compile.py", f"{protocol}.mpc"])

    subprocess.run(
            ["../Scripts/setup-ssl.sh", str(s_val)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

    for i in range(10):
        print(f"i = {i}")
        generate_ballots.main()

        try:
            result = subprocess.run(
                ["../Scripts/mascot.sh", protocol, "-N", str(s_val), "-IF", "Player-Data/matrix"],
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error at Candidate={c_val}, i={i}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}") # This will likely show "Mac Check Failed" or "Connection Refused"
            break
                
        with open(f"Outputs/candidates_repetition/output{"_leak" if leak else ""}-c{c_val}-s{s_val}-v{v_val}-f{f_val}.txt", "a") as f:
            f.write(result.stdout)


    