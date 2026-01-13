# Must be run from the "My_Scripts" Directory!

c_val="3"
s_val="3"
v_val="64"
f_val="1"
gen_ballots=true

while [ $c_val -le 20 ]; do
    echo "c_val = $c_val"
    ./run_script.sh -c $c_val -s $s_val -v $v_val -f $f_val -g $gen_ballots > "Outputs/candidates/output-c${c_val}-s${s_val}-v${v_val}-f${f_val}.txt" 2>&1
    ./run_script_leak.sh -c $c_val -s $s_val -v $v_val -f $f_val -g $gen_ballots > "Outputs/candidates/output-leak-c${c_val}-s${s_val}-v${v_val}-f${f_val}.txt" 2>&1
    c_val=$((c_val + 1))
done
