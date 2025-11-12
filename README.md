# To be written


# Note to self
Before running any code change the constants in  `My_scripts/consts.py` to match the desired setup
```bash
# 🧭 Navigate to your MP-SPDZ directory
cd Coding/mp-spdz-0.4.1

# 🗳️ Generate ballots
python My_scripts/generate_ballots.py

# ⚙️ Compile and execute the MPC protocol (3 players)
./compile.py My_scripts/rcv_matrix.mpc
Scripts/mascot.sh rcv_matrix -N 3 -IF My_scripts/Player-Data/matrix
```
Change `-N 3` to the number of parties needed (Must be the same as `NUM_PARTIES` in `My_scripts/consts.py`)
