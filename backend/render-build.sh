#!/bin/bash
# Make sure pip, setuptools, and wheel are up-to-date
python3.11 -m ensurepip --upgrade
python3.11 -m pip install --upgrade pip setuptools wheel

# Optional: add Rust if any package needs compilation
# curl https://sh.rustup.rs -sSf | sh -s -- -y
# export PATH="$HOME/.cargo/bin:$PATH"

# Install project dependencies
python3.11 -m pip install -r requirements.txt
