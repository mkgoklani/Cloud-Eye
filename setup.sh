#!/bin/bash

# Universal NVR - First Time Setup Script
# Usage: ./setup.sh

GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}[*] Starting Universal NVR Setup...${NC}"

# --- 1. OS Detection & System Dependencies ---
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "[-] Linux detected. Updating package lists..."
    sudo apt-get update -y
    
    echo "[-] Installing System Dependencies (libpcap, ffmpeg libs)..."
    # scapy needs libpcap; opencv needs ffmpeg libs
    sudo apt-get install -y python3-pip python3-venv libpcap-dev libgl1 libglib2.0-0
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "[-] macOS detected."
    # Mac usually has these, or user manages via Homebrew
    if ! command -v brew &> /dev/null; then
        echo "Warning: Homebrew not found. Ensure libpcap is installed if Scapy fails."
    fi
fi

# --- 2. Python Environment Setup ---
# It is best practice to create a Virtual Environment so we don't break system Python
if [ ! -d "venv" ]; then
    echo -e "${GREEN}[*] Creating Python Virtual Environment (venv)...${NC}"
    python3 -m venv venv
else
    echo "[-] venv already exists. Skipping."
fi

# Activate venv for the following commands
source venv/bin/activate

echo -e "${GREEN}[*] Installing Python Libraries from requirements.txt...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# --- 3. Directory & Permission Setup ---
echo -e "${GREEN}[*] Configuring Directories...${NC}"
mkdir -p storage
mkdir -p logs

echo "[-] Setting permissions for scripts..."
chmod +x scanner.py
chmod +x connector.py
chmod +x config_builder.py
chmod +x app.py

# --- 4. Docker Check ---
echo -e "${GREEN}[*] Checking Docker Environment...${NC}"
if command -v docker &> /dev/null; then
    echo "[-] Docker is installed."
else
    echo "r[!] WARNING: Docker is NOT installed."
    echo "    Please install Docker Desktop (Mac) or Docker Engine (Linux) manually."
fi

if command -v docker-compose &> /dev/null; then
    echo "[-] Docker Compose is installed."
else
    # Newer docker versions use 'docker compose' instead of 'docker-compose'
    if docker compose version &> /dev/null; then
        echo "[-] Docker Compose (plugin) is installed."
    else
        echo "[!] WARNING: Docker Compose is missing."
    fi
fi

# --- 5. Finish ---
echo -e "${GREEN}[*] Setup Complete!${NC}"
echo ""
echo "To start the system, actviate the environment and run the scripts:"
echo "  source venv/bin/activate"
echo "  sudo python3 scanner.py -t <subnet>"
echo ""