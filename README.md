# Secure Ranked Choice Voting Protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A secure multi-party computation (MPC) implementation of Ranked Choice Voting (RCV) using secret-shared matrices and the MP-SPDZ framework.

## Overview

This project implements a privacy-preserving Ranked Choice Voting protocol that allows multiple parties to jointly conduct an election without any single party learning individual voter preferences. The protocol uses Shamir secret sharing and secure multi-party computation techniques to ensure voter privacy while computing the correct election result.

### Key Features

- **Privacy-Preserving**: Voter preferences are never revealed to any individual party
- **Verifiable**: Uses Shamir secret sharing with configurable threshold for robustness
- **Efficient**: Implements optimized matrix-based RCV protocol using MP-SPDZ
- **Flexible**: Supports variable numbers of candidates, voters, servers, and field sizes
- **Malicious Model Support**: Optional information leakage variant for performance comparison

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
cd Coding/mp-spdz-0.4.1/My_scripts
chmod +x run_script.sh
./run_script.sh
```

This uses default parameters:
- 3 candidates
- 3 computing servers
- 5 votes
- Field size of 2¹

### Advanced Usage

Run with custom parameters:

```bash
./run_script.sh -c 5 -s 3 -v 100 -f 32
```

**Options:**
- `-c <num_candidates>`: Number of candidates (default: 3)
- `-s <num_servers>`: Number of computing servers (default: 3)
- `-v <num_votes>`: Number of votes (default: 5)
- `-f <field_size_bits>`: Field size in bits as power of 2 (default: 1, meaning 2¹)
- `-g <true|false>`: Generate new ballots or use existing (default: true)

### Output

The protocol generates:
- **Player-Data/**: Secret shares distributed among servers
- **Outputs/**: Election results and timing information
- **logs/**: Execution logs from the protocol




## Development

### Project Organization

- **rcv_matrix.mpc**: Core RCV protocol in MP-SPDZ's high-level language
- **generate_ballots.py**: Generates random RCV ballots for testing
- **run_simulation.py**: Batch testing script for performance evaluation
- **Shamir.py**: Implements Shamir secret sharing in Python for ballot generation


## References

This project implements protocols based on research in secure multi-party computation and electronic voting. Key related work:

- **MP-SPDZ Framework**: https://github.com/data61/MP-SPDZ
  - Multi-Protocol SPDZ framework for benchmarking MPC protocols
  - Marcel Keller. "MP-SPDZ: A Versatile Framework for Multi-Party Computation." CCS 2020.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- Mikkel Katholm - Aarhus University
- Emil Mors - Aarhus University

Built as part of a 9th semester project at Aarhus University, Department of Computer Science.
