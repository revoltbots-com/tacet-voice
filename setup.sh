#!/bin/bash

echo "========================================"
echo "Tacet - Setup (macOS/Linux)"
echo "========================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/downloads/"
    exit 1
fi

echo "[1/4] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "[2/4] Activating virtual environment..."
source venv/bin/activate

echo "[3/4] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# macOS-specific dependencies
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS - checking for additional dependencies..."
    # Check if portaudio is installed (needed for sounddevice)
    if ! brew list portaudio &> /dev/null; then
        echo "Installing portaudio via Homebrew..."
        brew install portaudio
    fi
fi

# Linux-specific dependencies
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux"
    echo "Note: If you encounter audio issues, you may need to install:"
    echo "  Ubuntu/Debian: sudo apt-get install portaudio19-dev python3-pyaudio"
    echo "  Fedora: sudo dnf install portaudio-devel"
fi

echo "[4/4] Creating config file..."
if [ ! -f config.json ]; then
    cp config.example.json config.json
    echo "Created config.json from example"
else
    echo "config.json already exists, skipping"
fi

echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "To run the application:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run the GUI: python stt_gui.py"
echo ""

# macOS-specific notice
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS IMPORTANT:"
    echo "  You will need to grant Accessibility permissions when first running."
    echo "  Go to: System Preferences → Security & Privacy → Privacy → Accessibility"
    echo "  Add Terminal or Python to the allowed apps."
    echo ""
fi

echo "Or simply run: ./start_gui.sh"
echo ""
