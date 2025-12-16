c_val="3"
s_val="2"
v_val="64"
f_val="1"
gen_ballots=true

while [ $s_val -le 6 ]; do
    echo "s_val = $s_val"
    ./../run_script_leak.sh -c $c_val -s $s_val -v $v_val -f $f_val -g $gen_ballots > "../Outputs/servers/output-leak-c${c_val}-s${s_val}-v${v_val}-f${f_val}.txt" 2>&1
    s_val=$((s_val + 1))
done
