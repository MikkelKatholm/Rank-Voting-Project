#!/bin/bash

gen_ballots=""
skip_build=false

usage () {
  echo "Usage: $0 -g <generate_ballots> [-s skip_rebuild]"
  echo ""
  echo "  -g true|false   Whether to generate ballots for clients"
  echo "  -s              Skip the make clean + rebuild (use after first build)"
  1>&2
  exit 1
}

while getopts "g:s" opt; do
  case $opt in
    g) gen_ballots="$OPTARG" ;;
    s) skip_build=true ;;
    *) usage ;;
  esac
done

if [ -z "$gen_ballots" ]; then
    echo "❌ Error: -g argument is required"
    usage
fi

set -e

set -a
source MASTER_Scripts/consts.env
set +a

# --- Configuration ---
N_PARTIES=$NUM_SERVERS
TOTAL_CLIENTS=$NUM_VOTERS
PROTOCOL="mascot"
FIELD_BITS=40
# ---------------------

if [ ! -f "compile.py" ]; then
    echo "❌ Error: Run from MP-SPDZ root."
    exit 1
fi

if ! python3 -c "import gmpy2" &> /dev/null; then
    echo "⚠️  Installing gmpy2..."
    pip3 install gmpy2
fi

# -----------------------------------------------------------------------
# STEP 1: Rebuild with SECURE = -DINSECURE
# -----------------------------------------------------------------------
if [ "$skip_build" = false ]; then
    echo "🔧 Configuring CONFIG.mine for fake preprocessing..."

    # Remove any old MY_CFLAGS = -DINSECURE lines (these cause compiler errors)
    if grep -q "MY_CFLAGS.*DINSECURE" CONFIG.mine 2>/dev/null; then
        echo "   ⚠️  Removing bad MY_CFLAGS = -DINSECURE line from CONFIG.mine"
        sed -i '/MY_CFLAGS.*DINSECURE/d' CONFIG.mine
    fi

    if ! grep -q "SECURE.*DINSECURE" CONFIG.mine 2>/dev/null; then
        echo "SECURE = -DINSECURE" >> CONFIG.mine
        echo "   ✅ Added SECURE = -DINSECURE to CONFIG.mine"
    else
        echo "   ℹ️  SECURE = -DINSECURE already present, skipping."
    fi

    # Only add -Wno-deprecated-literal-operator if clang supports it
    if echo "" | clang++ -Wno-deprecated-literal-operator -Werror -x c++ - -fsyntax-only 2>/dev/null; then
        if ! grep -q "Wno-deprecated-literal-operator" CONFIG.mine 2>/dev/null; then
            echo "MY_CFLAGS += -Wno-deprecated-literal-operator" >> CONFIG.mine
            echo "   ✅ Added -Wno-deprecated-literal-operator to CONFIG.mine"
        else
            echo "   ℹ️  -Wno-deprecated-literal-operator already present, skipping."
        fi
    else
        echo "   ℹ️  clang doesn't support -Wno-deprecated-literal-operator, skipping."
        sed -i '/Wno-deprecated-literal-operator/d' CONFIG.mine 2>/dev/null || true
    fi

    echo "--- CONFIG.mine now contains ---"
    cat CONFIG.mine
    echo "--------------------------------"

    echo "🔨 Rebuilding Fake-Offline.x and mascot-party.x..."
    make clean
    env -u DEBUG make -j8 Fake-Offline.x mascot-party.x
    echo "   ✅ Build complete."
else
    echo "⏩ Skipping rebuild (-s flag set)."
fi
# -----------------------------------------------------------------------
# STEP 2: Generate fake offline preprocessing data
# -----------------------------------------------------------------------
echo "🎲 Generating fake offline preprocessing data..."
Scripts/setup-online.sh $N_PARTIES $FIELD_BITS &> /dev/null
./Fake-Offline.x $N_PARTIES -e 1,40,41,79 &> /dev/null
echo "✅ Fake preprocessing data written to Player-Data/"


# Kill lingering processes
echo "🧹 Cleaning up lingering processes..."
lsof -ti:$PORTNUM 2>/dev/null | xargs kill -9 2>/dev/null || true
pkill -9 mascot-pa 2>/dev/null || true
sleep 1

# Generate ballots
if [ "$gen_ballots" = true ]; then
    echo "⚙️ Generating ballots for $TOTAL_CLIENTS clients..."
    python3 MASTER_Scripts/generate_ballots.py
    sleep 1
fi

# -----------------------------------------------------------------------
# STEP 3: Compile MPC program
# -----------------------------------------------------------------------
echo "🔨 Compiling MPC program..."
./compile.py -F 40 -b 100 MASTER_Scripts/RCV_server.mpc > /dev/null

# -----------------------------------------------------------------------
# STEP 4: Certs
# -----------------------------------------------------------------------
echo "🔐 Generating Certs..."
if [ "$DEBUG" -eq 0 ]; then
    Scripts/setup-ssl.sh $N_PARTIES &> /dev/null
    Scripts/setup-clients.sh $TOTAL_CLIENTS &> /dev/null
else
    Scripts/setup-ssl.sh $N_PARTIES
    Scripts/setup-clients.sh $TOTAL_CLIENTS
fi

# -----------------------------------------------------------------------
# STEP 5: Start MPC parties
# -----------------------------------------------------------------------
echo "🚀 Starting $N_PARTIES MPC parties (fake offline, -F flag)..."
PLAYERS=$N_PARTIES Scripts/$PROTOCOL.sh -F RCV_server &
MPC_PID=$!
sleep 2

# -----------------------------------------------------------------------
# STEP 6: Launch clients
# -----------------------------------------------------------------------

echo "👥 Launching $TOTAL_CLIENTS clients..."
for (( i=0; i<$TOTAL_CLIENTS; i++ )); do
    if [ "$i" -lt $((TOTAL_CLIENTS-1)) ]; then
        python3 MASTER_Scripts/RCV_client.py $i 0 &
    else
        python3 MASTER_Scripts/RCV_client.py $i 1 &
    fi
done

wait
echo "✅ Done."
kill $MPC_PID 2>/dev/null || true