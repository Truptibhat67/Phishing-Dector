#!/bin/bash
# Make sure pip, setuptools, and wheel are up-to-date
python -m ensurepip --upgrade
python -m pip install --upgrade pip setuptools wheel

# Optional: add Rust if any package needs compilation
# curl https://sh.rustup.rs -sSf | sh -s -- -y
# export PATH="$HOME/.cargo/bin:$PATH"

# Install project dependencies
python -m pip install -r requirements.txt
