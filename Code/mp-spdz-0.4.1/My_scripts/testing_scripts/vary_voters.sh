# Must be run from the "My_Scripts" Directory!

c_val="3"
s_val="3"
v_val="10"
f_val="1"
gen_ballots=true

while [ $v_val -le 1000 ]; do
    echo "v_val = $v_val"
    ./run_script.sh -c $c_val -s $s_val -v $v_val -f $f_val -g $gen_ballots > "Outputs/voter/output-c${c_val}-s${s_val}-v${v_val}-f${f_val}.txt" 2>&1
    ./run_script_leak.sh -c $c_val -s $s_val -v $v_val -f $f_val -g $gen_ballots > "Outputs/voter/output-leak-c${c_val}-s${s_val}-v${v_val}-f${f_val}.txt" 2>&1
    v_val=$((v_val + 10))
done
