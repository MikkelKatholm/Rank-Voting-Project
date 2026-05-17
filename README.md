# Secure Ranked Choice Voting Protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A secure multi-party computation (MPC) implementation of Ranked Choice Voting (RCV) using secret-shared matrices and the MP-SPDZ framework.

## Overview

This project implements a privacy-preserving Ranked Choice Voting protocol that allows multiple parties to jointly conduct an election without any single party learning individual voter preferences. The protocol uses Shamir secret sharing and secure multi-party computation techniques to ensure voter privacy while computing the correct election result.

## Project Structure

```
Rank-Voting-Project/
└── Code/                             # Core implementation
    └── mp-spdz-0.4.1/
        └── My_scripts/               # Project-specific scripts
            ├── rcv_matrix.mpc        # Main RCV protocol
            ├── rcv_matrix_leak.mpc   # Variant with controlled leakage
            ├── run_script.sh         # Main execution script
            ├── generate_ballots.py   # Ballot generation
            ├── Shamir.py             # Shamir secret sharing implementation
            └── consts.py             # Configuration constants
```

## Quick Start

### Prerequisites

- Linux-based system
- Python 3.7+
- C++ compiler (g++ or clang)
- Make
- OpenSSL development libraries
- Standard build tools (gcc, automake, etc.)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Rank-Voting-Project
   ```

2. **Build MP-SPDZ**

    Refer to the [MP-SPDZ Documentation](https://mp-spdz.readthedocs.io/en/latest/) for detailed build instructions

### Basic Usage

Run a complete RCV election with default parameters:

```bash
cd Coding/mp-spdz-0.4.1/
chmod +x MASTER_Scripts/run_RCV.sh
./MASTER_Scripts/run_RCV.sh -g true
# or 
./MASTER_Scripts/run_RCV_fake_offline.sh -g true
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

