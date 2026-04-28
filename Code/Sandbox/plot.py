import math
import matplotlib.pyplot as plt

def f(x):
    term = 1  # P(x,0)
    s = 1

    for k in range(1, x + 1):
        term *= (x - k + 1)  # build P(x,k) iteratively
        s += term

    return math.log2(s)

xs = range(100, 500)
ys = [f(x) for x in xs]

plt.plot(xs, ys)
plt.xlabel("x")
plt.ylabel("f(x)")
plt.title("Stable computation of log2 sum of permutations")
plt.grid(True)
plt.show()