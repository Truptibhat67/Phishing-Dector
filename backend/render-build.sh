#!/bin/bash
set -e

# Install project dependencies
python -m pip install -r requirements.txt

# Ensure uvicorn is installed
python -m pip install uvicorn
