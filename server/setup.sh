#!/bin/bash

# Voice Agent Setup Script
# This script sets up the Python virtual environment and installs dependencies

echo "Setting up Voice Agent development environment..."

# Check if Python 3.10+ is installed
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.10 or higher is required. Current version: $python_version"
    echo "Please upgrade Python or use a different Python version."
    exit 1
fi

echo "Python version: $python_version ✓"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create audio directory
echo "Creating audio directory..."
mkdir -p audio

# Create .env file if it doesn't exist in parent directory
if [ ! -f ../.env ]; then
    echo "Creating .env file from template in parent directory..."
    cp ../env.example ../.env
    echo "Please edit ../.env file with your AWS credentials"
else
    echo "Found .env file in parent directory ✓"
fi

echo ""
echo "Setup complete! 🎉"
echo ""
echo "To start development:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the server: python run.py"
echo "3. Or use uvicorn directly: uvicorn app.main:app --reload"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Note: .env file is located in the parent directory (~/livekit/vagent/.env)" 