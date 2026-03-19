from Crypto.Random import random as crypto_random

l = [1, 2, 3, 4, 5]

print(f"Original list: {l}")

perm = list(range(len(l)))
crypto_random.shuffle(perm)
print(f"Shuffled indices: {perm}")

inv_perm = [0 for _ in range(len(l))]
for i, num in enumerate(perm):
    inv_perm[num] = i

print(f"Inverse permutation: {inv_perm}")

l = [l[i] for i in perm]
print(f"Shuffled list: {l}")

l = [l[i] for i in inv_perm]
print(f"Restored list: {l}")