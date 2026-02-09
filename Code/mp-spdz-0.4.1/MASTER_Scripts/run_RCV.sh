#!/bin/bash

# Exit on error
set -e

# --- Configuration ---
N_PARTIES=2           # Number of MPC servers
TOTAL_CLIENTS=1      # Set this to however many clients you want
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
./compile.py MASTER_Scripts/RCV_server.mpc > /dev/null

echo "🔐 Generating Certs..."
Scripts/setup-ssl.sh $N_PARTIES > /dev/null
Scripts/setup-clients.sh $TOTAL_CLIENTS > /dev/null

# 3. Start MPC Servers
echo "🚀 Starting $N_PARTIES MPC parties..."
PLAYERS=$N_PARTIES Scripts/$PROTOCOL.sh RCV_server &
MPC_PID=$!
sleep 2

# 4. Launch Clients with Random Inputs
echo "👥 Launching $TOTAL_CLIENTS clients"

for (( i=0; i<$TOTAL_CLIENTS; i++ ))
do
    python3 MASTER_Scripts/RCV_client.py $i $N_PARTIES 1 &
done

# 5. Cleanup
wait
echo "✅ Done."
kill $MPC_PID 2>/dev/null || true