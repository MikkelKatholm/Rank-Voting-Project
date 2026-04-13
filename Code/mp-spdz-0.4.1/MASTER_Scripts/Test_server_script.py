from pathlib import Path
from dotenv import load_dotenv, set_key
import subprocess
import re
import pandas as pd



SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CONSTS_FILE = SCRIPT_DIR / "consts.env"

import sys
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from consts import TIMER_IDS, dict_value_to_key


def main():
    servers = [i for i in range(2,11)]
    clients = [2**i for i in range(2,21)]
    candidates = [2*i for i in range(2,11)]
    run_leak_version = [0, 1]

    results = []


    for num_servers in servers:
        for num_clients in clients:
            for num_cands in candidates:
                for leak_version in run_leak_version:
                    print(f"Running with {num_servers} servers, {num_clients} clients, {num_cands} candidates, leak version: {leak_version}")
                    # Update the .env file with the new values
                    consts = {
                        "NUM_SERVERS": num_servers,
                        "NUM_VOTERS": num_clients,
                        "NUM_CANDS": num_cands,
                        "RUN_LEAK_VERSION": leak_version
                    }
                    update_consts(consts)

                    # Run the test script
                    result = subprocess.run(
                        ["bash", str(SCRIPT_DIR / "run_RCV.sh"), "-g", "true"],
                        cwd=REPO_ROOT,
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    row_data = parse_output(result.stdout, consts)
                    results.append(row_data)

                    # Save incrementally in case of crash
                    df = pd.DataFrame(results)
                    df.to_csv(SCRIPT_DIR / "benchmark_results.csv", index=False, sep=";")


def update_consts(consts: dict):
    if not CONSTS_FILE.exists():
        raise FileNotFoundError(f"No consts.env file found at {CONSTS_FILE}")

    load_dotenv(CONSTS_FILE, override=True)

    for key, value in consts.items():
        set_key(str(CONSTS_FILE), key, str(value), quote_mode="never")

    load_dotenv(CONSTS_FILE, override=True)


def parse_output(output: str, run_params: dict) -> dict:
    row = run_params.copy()
    
    # Initialize default keys
    row['total_time_s'] = None
    row['data_sent_mb'] = None
    row['data_sent_rounds'] = None
    row['global_data_sent_mb'] = None
    
    for line in output.splitlines():
        line = line.strip()
        
        if line.startswith("Time ="):
            m = re.search(r"Time = ([\d.]+) seconds", line)
            if m:
                row['total_time_s'] = float(m.group(1))
                
        elif line.startswith("Time") and "seconds" in line:
            m = re.search(r"Time(\d+) = ([\d.]+) seconds \(([\d.]+) MB, (\d+) rounds\)", line)
            if m:
                timer_id = int(m.group(1))
                time_s = float(m.group(2))
                data_mb = float(m.group(3))
                rounds = int(m.group(4))
                
                timer_name = dict_value_to_key(TIMER_IDS, timer_id)
                row[f"{timer_name}_time_s"] = time_s
                row[f"{timer_name}_data_mb"] = data_mb
                row[f"{timer_name}_rounds"] = rounds
                
        elif line.startswith("Data sent ="):
            m = re.search(r"Data sent = ([\d.]+) MB in ~(\d+) rounds", line)
            if m:
                row['data_sent_mb'] = float(m.group(1))
                row['data_sent_rounds'] = int(m.group(2))
                
        elif line.startswith("Global data sent ="):
            m = re.search(r"Global data sent = ([\d.]+) MB", line)
            if m:
                row['global_data_sent_mb'] = float(m.group(1))
    return row


if __name__ == "__main__":
    main()