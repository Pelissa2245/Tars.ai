#!/bin/bash

PROJECT_DIR="/home/matheus/Tars.ai"
VENV_DIR="$PROJECT_DIR/Tars.ai"
SCRIPT_FILE="$PROJECT_DIR/tars_assistant.py"

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv "$VENV_DIR"
    exit 1
fi

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"

echo "Starting Tars Assistant..."
python3 "$SCRIPT_FILE"

deactivate