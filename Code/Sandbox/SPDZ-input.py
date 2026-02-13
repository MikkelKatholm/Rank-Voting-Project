import random

SERVERS = 3
PRIME = 5


def generate_shares(secret):
    """Generate additive shares of a secret mod PRIME."""
    shares = []
    for _ in range(SERVERS - 1):
        share = random.randint(0, PRIME - 1)
        shares.append(share)

    final_share = (secret - sum(shares)) % PRIME
    shares.append(final_share)

    return shares


def reconstruct_secret(shares):
    """Reconstruct secret from additive shares."""
    return sum(shares) % PRIME


def get_random_value():
    """Simulate preprocessing: servers obtain shared random value <s>."""
    random_secret = random.randint(0, PRIME - 1)
    return generate_shares(random_secret)


# Protocol Input Supply (Damgård et al.)
def protocol_input_supply(secret):
    print(f"\nSecret to input: {secret}")

    # Step 1: Servers obtain random shared value <s>
    s_shares = get_random_value()
    s = reconstruct_secret(s_shares)

    print(f"Random shared value <s>: {s_shares}")
    print(f"Reconstructed s: {s}")

    # Step 2: Client computes masked input (x - s)
    masked_input = (secret - s) % PRIME
    print(f"Client broadcasts (x - s): {masked_input}")

    # Step 3: Servers compute <x> = <s> + (x - s)
    # IMPORTANT: Add public value to only ONE share
    x_shares = []

    for i in range(SERVERS):
        if i == 0:
            new_share = (s_shares[i] + masked_input) % PRIME
        else:
            new_share = s_shares[i]

        x_shares.append(new_share)
        print(f"Server {i + 1} final share of x: {new_share}")

    # Reconstruction check
    reconstructed_x = reconstruct_secret(x_shares)
    print(f"Reconstructed x from shares: {reconstructed_x}")

    if reconstructed_x == secret:
        print("Protocol successful: shares reconstruct to original secret.")
    else:
        print("Something went wrong.")


if __name__ == "__main__":
    secret = int(input(f"Enter the secret input (0 to {PRIME - 1}): "))
    if 0 <= secret < PRIME:
        protocol_input_supply(secret)
    else:
        print(f"Please enter a valid secret input between 0 and {PRIME - 1}.")
