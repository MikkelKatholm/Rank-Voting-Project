#!/bin/bash

# Arguments:
gen_ballots=""

usage () {
  echo "Usage: $0 -g <generate_ballots>"
  1>&2
  exit 1
}
while getopts "g:" opt; do
  case $opt in
    g) gen_ballots="$OPTARG"
        ;;
    *) usage
        ;;
  esac
done

# Check if -g argument was provided
if [ -z "$gen_ballots" ]; then
    echo "❌ Error: -g argument is required"
    usage
fi

# Exit on error
set -e

set -a          # automatically export all variables
source MASTER_Scripts/consts.env
set +a

# --- Configuration ---
N_PARTIES=$NUM_SERVERS              # Number of MPC servers
TOTAL_CLIENTS=$NUM_VOTERS           # Set this to however many clients you want
PROTOCOL="mascot"                   # Arithmetic protocol
# ---------------------

# Validation & Setup
if [ ! -f "compile.py" ]; then
    echo "❌ Error: Run from MP-SPDZ root."
    exit 1
fi

if ! python3 -c "import gmpy2" &> /dev/null; then
    echo "⚠️  Installing gmpy2..."
    pip3 install gmpy2
fi


# Kill any lingering processes on the port
# Nuke every mascot-pa processes
echo "🧹 Cleaning up any existing processes on port $PORTNUM and mascot-pa processes..."
lsof -ti:$PORTNUM 2>/dev/null | xargs kill -9 2>/dev/null || true
pkill -9 mascot-pa 2>/dev/null || true
sleep 1

# Generate the ballots for clients
if [ "$gen_ballots" = true ]; then
    echo "⚙️ Generating ballots for $TOTAL_CLIENTS clients..."
    python3 MASTER_Scripts/generate_ballots.py
    sleep 1
fi

# Compile & Certs
echo "🔨 Compiling..."
./compile.py MASTER_Scripts/RCV_server.mpc > /dev/null

echo "🔐 Generating Certs..."
if [ "$DEBUG" -eq 0 ]; then
    Scripts/setup-ssl.sh $N_PARTIES &> /dev/null
    Scripts/setup-clients.sh $TOTAL_CLIENTS &> /dev/null
else
    Scripts/setup-ssl.sh $N_PARTIES
    Scripts/setup-clients.sh $TOTAL_CLIENTS
fi

# Start MPC Servers
echo "🚀 Starting $N_PARTIES MPC parties..."
PLAYERS=$N_PARTIES Scripts/$PROTOCOL.sh RCV_server &
MPC_PID=$!
sleep 2

# Launch Clients with Random Inputs
echo "👥 Launching $TOTAL_CLIENTS clients"

for (( i=0; i<$TOTAL_CLIENTS; i++ ))
do
    if [ "$i" -lt $((TOTAL_CLIENTS-1)) ]; then
        python3 MASTER_Scripts/RCV_client.py $i 0 &
    else
        python3 MASTER_Scripts/RCV_client.py $i 1 &
    fi
done

# Cleanup
wait
echo "✅ Done."
kill $MPC_PID 2>/dev/null || true