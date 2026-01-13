# reconstruct.py
import struct
from consts import *

PRIME = FIELD_SIZE

def read_share(pid):
    with open(f"Player-Data/Memory-p-P{pid}", "rb") as f:
        data = f.read()

    # Skip text header if present
    header_end = data.find(b'\n\x00')
    if header_end != -1:
        data = data[header_end + 2:]
    
    # Try reading 16 bytes (128-bit) little-endian unsigned integer
    if len(data) >= 16:
        share_val = int.from_bytes(data[:16], "little")
    else:
        share_val = int.from_bytes(data, "little")

    return share_val % PRIME


shares = [(i+1, read_share(i)) for i in range(3)]

def lagrange_interpolate(x, x_s, y_s, p):
    k = len(x_s)
    total = 0
    for i in range(k):
        xi, yi = x_s[i], y_s[i]
        li = 1
        for j in range(k):
            if i != j:
                li = (li * (x - x_s[j]) * pow(xi - x_s[j], -1, p)) % p
        total = (total + yi * li) % p
    return total

reconstructed_secret = lagrange_interpolate(
    0,
    [x for x, _ in shares],
    [y for _, y in shares],
    PRIME,
)

print("Shares:")
for i, s in shares:
    print(f"  P{i}: {s}")
print(f"\nReconstructed secret: {reconstructed_secret}")
