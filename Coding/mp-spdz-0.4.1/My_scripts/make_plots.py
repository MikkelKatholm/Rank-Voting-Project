import matplotlib.pyplot as plt
import numpy as np
import os
import re
import math
from matplotlib.ticker import MaxNLocator
from collections import defaultdict


def find_v(s):
    match = re.search(r"v(\d+)", s)
    if match:
        number = int(match.group(1))
        return number
    
def find_s(s):
    match = re.search(r"s(\d+)", s)
    if match:
        number = int(match.group(1))
        return number
    
def find_c(s):
    match = re.search(r"c(\d+)", s)
    if match:
        number = int(match.group(1))
        return number

def plot_varying_candidates():
    times = dict()
    times_leak = dict()

    for file_name in os.listdir("Outputs/candidates"):
        with open(f"Outputs/candidates/{file_name}", "r") as f:
            file_content = f.read()

        match = re.search(r"Time\s*=\s*([0-9.]+)\s*seconds", file_content)
        if match:
            time_value = float(match.group(1))
            c = find_c(file_name)

            if "leak" in file_name:
                times_leak[c] = time_value
            else:
                times[c] = time_value

    x_values = sorted(times.keys())
    y_values = [(times[x]/x**5) for x in x_values]

    x_values_leak = sorted(times_leak.keys())
    y_values_leak = [(times_leak[x]/x**5) for x in x_values_leak]

    plt.plot(x_values, y_values, marker='o', label="No Leak")
    plt.plot(x_values_leak, y_values_leak, marker='x', label="Leak")

    plt.xlabel(r"$c$")
    plt.ylabel("Time (seconds)")
    plt.legend()
    plt.show()

def plot_varying_servers():
    times = dict()
    times_leak = dict()

    for file_name in os.listdir("Outputs/servers"):
        with open(f"Outputs/servers/{file_name}", "r") as f:
            file_content = f.read()

        match = re.search(r"Time\s*=\s*([0-9.]+)\s*seconds", file_content)
        if match:
            time_value = float(match.group(1))
            s = find_s(file_name)

            if "leak" in file_name:
                times_leak[s] = time_value
            else:
                times[s] = time_value

    x_values = sorted(times.keys())
    y_values = [times[x] for x in x_values]

    x_values_leak = sorted(times_leak.keys())
    y_values_leak = [times_leak[x] for x in x_values_leak]

    plt.plot(x_values, y_values, marker='o', label="No Leak")
    plt.plot(x_values_leak, y_values_leak, marker='x', label="Leak")
    plt.title("Running time of election with 3 candidates and 64 voters")
    plt.xlabel("Number of servers")
    plt.ylabel("Average running time of election (s)")
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.legend()
    file_name = "election_varying_servers"
    plt.savefig(f"Outputs/figures/{file_name}")


def plot_varying_voters():
    times = dict()
    times_leak = dict()

    for file_name in os.listdir("Outputs/voter"):
        with open(f"Outputs/voter/{file_name}", "r") as f:
            file_content = f.read()

        match = re.search(r"Time\s*=\s*([0-9.]+)\s*seconds", file_content)
        if match:
            time_value = float(match.group(1))
            v = find_v(file_name)
            if v >= 200:
                continue

            if "leak" in file_name:
                times_leak[v] = time_value
            else:
                times[v] = time_value
        else:
            if "leak" in file_name:
                print(f"⚠ No time found in {file_name}")

    x_values = sorted(times.keys())
    y_values = [times[x] for x in x_values]

    x_values_leak = sorted(times_leak.keys())
    y_values_leak = [times_leak[x] for x in x_values_leak]

    plt.plot(x_values, y_values, marker='o', label="No Leak")
    plt.plot(x_values_leak, y_values_leak, marker='x', label="Leak")
    plt.xlabel("Number of voters")
    plt.ylabel("Running time (s)")
    plt.legend()
    plt.savefig(f"Outputs/figures/varying_voters")

def get_values(s):
    pattern = r"([a-z])(\d+)"
    
    matches = re.findall(pattern, s)
    
    return {letter: int(value) for letter, value in matches}

def get_times(s):
    pattern = r"Time =\s*(\d+\.\d+)"

    times = re.findall(pattern, s)

    return [float(t) for t in times]

def rep_voters():
    base_dir = "Outputs/voters_repetition"

    avg_times = {"leak": {}, "no_leak": {}}
    all_times = {"leak": defaultdict(list), "no_leak": defaultdict(list)}

    for file_name in os.listdir(base_dir):
        path = os.path.join(base_dir, file_name)

        v = get_values(file_name)["v"]
        times = get_times(open(path).read())

        key = "leak" if "leak" in file_name else "no_leak"

        avg_times[key][v] = sum(times) / len(times)
        all_times[key][v].extend(times)

    def flatten(data):
        x_vals, y_vals = [], []
        for x, ys in data.items():
            x_vals.extend([x] * len(ys))
            y_vals.extend(ys)
        return x_vals, y_vals

    # Scatter (all runs)
    x_all, y_all = flatten(all_times["no_leak"])
    x_all_leak, y_all_leak = flatten(all_times["leak"])

    plt.plot(x_all, y_all, marker="o", ls="none", label="No leak")
    plt.plot(x_all_leak, y_all_leak, marker="x", ls="none", label="Leak", color="salmon")

    # Averages
    x_avg = sorted(avg_times["no_leak"])
    y_avg = [avg_times["no_leak"][x] for x in x_avg]
    plt.plot(x_avg, y_avg, color="blue")

    x_avg_leak = sorted(avg_times["leak"])
    y_avg_leak = [avg_times["leak"][x] for x in x_avg]
    plt.plot(x_avg_leak, y_avg_leak, color="red")
    plt.xlabel("Number of voters")
    plt.ylabel("Running time (s)")

    plt.legend()
    plt.savefig("Outputs/figures/vary_voters_all", dpi=400)


def make_plot(plot_name):
    base_dir = f"Outputs/{plot_name}_repetition"

    avg_times = {"leak": {}, "no_leak": {}}
    all_times = {"leak": defaultdict(list), "no_leak": defaultdict(list)}

    for file_name in os.listdir(base_dir):
        path = os.path.join(base_dir, file_name)

        value = get_values(file_name)[plot_name[0]]
        times = get_times(open(path).read())

        key = "leak" if "leak" in file_name else "no_leak"

        avg_times[key][value] = sum(times) / len(times)
        all_times[key][value].extend(times)

    def flatten(data):
        x_vals, y_vals = [], []
        for x, ys in data.items():
            x_vals.extend([x] * len(ys))
            y_vals.extend(ys)
        return x_vals, y_vals

    # Scatter (all runs)
    x_all, y_all = flatten(all_times["no_leak"])
    x_all_leak, y_all_leak = flatten(all_times["leak"])

    plt.plot(x_all, y_all, marker="o", ls="none", label="No leak")
    plt.plot(x_all_leak, y_all_leak, marker="x", ls="none", label="Leak", color="salmon")

    # Averages
    x_avg = sorted(avg_times["no_leak"])
    y_avg = [avg_times["no_leak"][x] for x in x_avg]
    plt.plot(x_avg, y_avg, color="blue")

    x_avg_leak = sorted(avg_times["leak"])
    y_avg_leak = [avg_times["leak"][x] for x in x_avg]
    plt.plot(x_avg_leak, y_avg_leak, color="red")
    plt.xlabel(f"Number of {plot_name}")
    plt.ylabel("Running time (s)")

    plt.legend()
    plt.savefig(f"Outputs/figures/vary_{plot_name}_all", dpi=400)

make_plot("candidates")