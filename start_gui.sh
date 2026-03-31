#!/bin/bash

echo "Starting Tacet GUI..."
echo ""

# Check if virtual environment exists
if [ ! -f venv/bin/activate ]; then
    echo "ERROR: Virtual environment not found"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment and run GUI
source venv/bin/activate
python stt_gui.py

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "Application exited with an error"
    read -p "Press Enter to continue..."
fi
