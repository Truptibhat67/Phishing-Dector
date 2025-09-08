curl https://sh.rustup.rs -sSf | sh -s -- -y
export PATH="$HOME/.cargo/bin:$PATH"
#!/bin/bash
python -m pip install --upgrade pip
pip install -r requirements.txt