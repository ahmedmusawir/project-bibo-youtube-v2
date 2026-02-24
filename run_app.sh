#!/bin/bash
# Launch VidGen Streamlit App

echo "🚀 Starting VidGen Streamlit App..."
echo "📂 Project: $(pwd)"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

streamlit run app/main.py
