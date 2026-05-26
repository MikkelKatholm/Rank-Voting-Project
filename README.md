# Secure Ranked Choice Voting Protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A secure multi-party computation (MPC) implementation of Ranked Choice Voting (RCV) using secret-shared matrices and the MP-SPDZ framework.

## Overview

This project implements a privacy-preserving Ranked Choice Voting protocol that allows multiple parties to jointly conduct an election without any single party learning individual voter preferences.

## Project Structure

```
Rank-Voting-Project/
└── Code/                             # Core implementation
    ├── mp-spdz-0.4.1/
    │   └── MASTER_Scripts/             # Project-specific scripts
    │       ├── RCV_clean_ballots.py    # Subprocess for validating ballots
    │       ├── RCV_client.py           # Client-side logic for ballot submission
    │       ├── RCV_convert_ballots.py  # Subprocess for converting sbit to sint
    │       ├── RCV_server.mpc          # Server-side logic for vote tallying
    │       ├── RCV_tally_no_leak.py    # Subprocess for tallying votes without leaking information
    │       ├── RCV_tally_round_leak.py # Subprocess for tallying votes with round information leakage
    │       ├── run_RCV.sh              # Script to run the RCV protocol with real offline phase
    │       ├── run_RCV_fake_offline.sh # Script to run the RCV protocol with a fake offline phase
    │       └── consts.py               # Configuration constants
    ├── Mix_nets/
    │   ├── run.py                      # Script to run the mix-net implementation
    │   ├── ...                         # Additional scripts and modules for mix-nets
    │   └── Consts_script.py            # Configuration constants for mix-nets
    └── Plot_making/
        ├── *.py                        # Scripts for generating plots and visualizations
        └── *.csv                       # Raw data from experiments for plotting
```

## Quick Start
0. **Prerequisites**
   - Refer to the [MP-SPDZ Documentation](https://mp-spdz.readthedocs.io/en/latest/) for prerequisites and setup instructions.
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Rank-Voting-Project
   ```

2. **Build MP-SPDZ**

    Refer to the [MP-SPDZ Documentation](https://mp-spdz.readthedocs.io/en/latest/) for detailed build instructions


## Basic Usage

Edit the `consts.env` file in the `MASTER_Scripts` directory to configure the protocol parameters (e.g., number of parties, number of candidates, etc.). To edit the backend protocol (MASCOT is used by default), modify the `run_RCV.sh` and `run_RCV_fake_offline.sh` scripts to specify the desired backend. 

> Note: If you want to use a different backend, ensure that the necessary setup and configuration for that backend are completed as per the MP-SPDZ documentation.

### Run the protocol with real offline phase
The `-g true` flag in the command indicates that a fresh set of random ballots will be generated for each run, if set to `false`, the same set of ballots from the last ballot generation will be used.
```bash
cd Code/mp-spdz-0.4.1/
chmod +x MASTER_Scripts/run_RCV.sh
./MASTER_Scripts/run_RCV.sh -g true|false
```

### Run the protocol with a fake offline phase
When running the protocol with a fake offline phase, leave the `-s` flag out for the first run to generate run the setup phase and generate the necessary random values. For subsequent runs, include the `-s` flag to skip the setup phase.
```bash
cd Code/mp-spdz-0.4.1/
chmod +x MASTER_Scripts/run_RCV_fake_offline.sh
# For the first run, use:
./MASTER_Scripts/run_RCV_fake_offline.sh -g true|false 
# For subsequent runs, use:
./MASTER_Scripts/run_RCV_fake_offline.sh -g true|false -s
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

