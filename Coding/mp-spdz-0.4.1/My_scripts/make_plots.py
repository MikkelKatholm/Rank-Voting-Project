import matplotlib.pyplot as plt
import numpy as np
import os
import re
import math

file_list = os.listdir("Outputs")

def find_v(s):
    match = re.search(r"v(\d+)", s)
    if match:
        number = int(match.group(1))
        return number

# files_list_sorted = sorted(file_list, key=lambda s: find_v(s))

times = dict()
times_leak = dict()

for file_name in file_list:
    with open(f"Outputs/{file_name}", "r") as f:
        file_content = f.read()

    match = re.search(r"Time\s*=\s*([0-9.]+)\s*seconds", file_content)
    if match:
        time_value = float(match.group(1))
        v = find_v(file_name)

        if "leak" in file_name:
            print(file_name, time_value)
            times_leak[v] = time_value
        else:
            times[v] = time_value
    else:
        if "leak" in file_name:
            print(f"⚠ No time found in {file_name}")

print(times)

x_values = sorted(times.keys())
y_values = [times[x] for x in x_values]

x_values_leak = sorted(times_leak.keys())
y_values_leak = [times_leak[x] for x in x_values_leak]

plt.plot(x_values, y_values, marker='o', label="No Leak")
plt.plot(x_values_leak, y_values_leak, marker='x', label="Leak")
plt.legend()
plt.xscale("log", base=2)
plt.yscale("log", base=2)
plt.show()