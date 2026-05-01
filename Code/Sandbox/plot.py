import re
import pandas as pd
TIMER_IDS = {
    "send_and_receive_ballots": 10,
    "clean_ballots": 11,
    "convert_ballots": 12,
    "tally": 13,
}


def dict_value_to_key(d: dict, value):
    for k, v in d.items():
        if v == value:
            return k
    raise ValueError(f"Value {value} not found in dictionary")


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

# parse output saved in t.txt and print the result
if __name__ == "__main__":
    with open("t.txt", "r") as f:
        output = f.read()
    
    consts = {
        "NUM_SERVERS": 5,
        "NUM_VOTERS": 32,
        "NUM_CANDS": 10,
        "RUN_LEAK_VERSION": 0,
    }
    
    results = [parse_output(output, consts)]
    df = pd.DataFrame(results)
    df.to_csv("benchmark_results.csv", index=False, sep=";")