#!/bin/bash
# Launch VidGen Streamlit App

echo "🚀 Starting VidGen Streamlit App..."
echo "📂 Project: $(pwd)"
echo ""

# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run streamlit using venv's python directly (bypasses pyenv shims)
.venv/bin/python -m streamlit run app/main.py
