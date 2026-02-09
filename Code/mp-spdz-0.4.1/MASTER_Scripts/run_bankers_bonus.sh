#!/bin/bash

# Exit on error
set -e

# --- Configuration ---
N_PARTIES=2           # Number of MPC servers
TOTAL_CLIENTS=101      # Set this to however many clients you want
PROTOCOL="mascot"     # Arithmetic protocol
# ---------------------

# 1. Validation & Setup
if [ ! -f "compile.py" ]; then
    echo "❌ Error: Run from MP-SPDZ root."
    exit 1
fi

if ! python3 -c "import gmpy2" &> /dev/null; then
    echo "⚠️  Installing gmpy2..."
    pip3 install gmpy2
fi

# 2. Compile & Certs
# Note: '1' here is a program argument for bankers_bonus (often used for rounds/setup), 
# it does NOT limit the client count to 1.
echo "🔨 Compiling..."
./compile.py bankers_bonus 1 > /dev/null

echo "🔐 Generating Certs..."
Scripts/setup-ssl.sh $N_PARTIES > /dev/null
Scripts/setup-clients.sh $TOTAL_CLIENTS > /dev/null

# 3. Start MPC Servers
echo "🚀 Starting $N_PARTIES MPC parties..."
PLAYERS=$N_PARTIES Scripts/$PROTOCOL.sh bankers_bonus-1 &
MPC_PID=$!
sleep 2

# 4. Launch Clients with Random Inputs
echo "👥 Launching $TOTAL_CLIENTS clients with random inputs..."

for (( i=0; i<$TOTAL_CLIENTS; i++ ))
do
    # Generate random input between 1000 and 9999
    INPUT_VAL=$((1000 + RANDOM % 9000))
    
    # Determine if this is the last client (to send the finish flag)
    if [ $i -eq $((TOTAL_CLIENTS - 1)) ]; then
        FINISH_FLAG=1
        echo "   -> Client $i (Last) : Input $INPUT_VAL | Finish Flag: 1"
    else
        FINISH_FLAG=0
        echo "   -> Client $i        : Input $INPUT_VAL | Finish Flag: 0"
    fi

    # Run client in background
    # args: client_id, n_parties, input_value, finish_flag
    python3 ExternalIO/bankers-bonus-client.py $i $N_PARTIES $INPUT_VAL $FINISH_FLAG &
done

# 5. Cleanup
wait
echo "✅ Done."
kill $MPC_PID 2>/dev/null || true