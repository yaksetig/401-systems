#!/bin/bash
set -e

echo "Installing Rust..."
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source ~/.cargo/env

echo "Installing circomspect..."
cargo install circomspect

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Build complete!"
