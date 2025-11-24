
c_val="3"
s_val="3"
v_val="5"
f_val="1"
gen_ballots=true

usage() {
  echo "Usage: $0 -c <num_candidates> -s <num_servers> -v <num_votes> -f <field_size_in_bits> -g <generate_ballots>"
  1>&2
  exit 1
}

while getopts "c:s:v:f:g:" opt; do
  case $opt in
    c) c_val="$OPTARG"
        ;;
    s) s_val="$OPTARG"
        ;;
    v) v_val="$OPTARG"
        ;;
    f) f_val="$OPTARG"
        ;;
    g) gen_ballots="$OPTARG"
        ;;
    *) usage
    ;;
  esac
done

# Write the constants to consts.py
file_contents="NUM_CANDIDATES = $c_val
NUM_PARTIES = $s_val
NUM_VOTES = $v_val
FIELD_SIZE = 2**$f_val
NUM_SHARES = NUM_PARTIES
THRESHOLD = NUM_PARTIES"

echo "$file_contents" > consts.py

if [ "$gen_ballots" = true ] ; then
    python3 generate_ballots.py
else
    echo "Skipping ballot generation."
fi

./../compile.py rcv_matrix_leak.mpc

../Scripts/mascot.sh rcv_matrix_leak -N $s_val -IF Player-Data/matrix