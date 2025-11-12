
NUM_CANDIDATES = 3
NUM_PARTIES = 3
NUM_VOTES = 5

## For shamir
FIELD_SIZE = 2**31 - 1  # To use with numbers larger then 2^64 the program must be compiled with the flag -F {field_size in bits}
#FIELD_SIZE = 1613
NUM_SHARES = NUM_PARTIES
THRESHOLD = NUM_PARTIES
