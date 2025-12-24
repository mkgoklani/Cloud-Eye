Markdown

# Universal NVR System

**A multi-stage Python & Docker framework for discovering, normalizing, and viewing IP cameras from any vendor.**
*Scan, Auto-Discover, Normalize, and Record IP Cameras from any vendor.*

---

## Project Overview

This system solves the fragmentation in the IP camera market by acting as a universal translation layer. It automates the entire lifecycle of a Network Video Recorder (NVR):

1.  **Discovery (The Hunter):** Finds devices on the LAN via ARP scanning (Layer 2).
2.  **Connection (The Diplomat):** Negotiates RTSP streams via ONVIF, Brute-force, or Vendor Hacks.
3.  **Ingestion (The Normalizer):** Feeds streams into a Go2RTC/FFmpeg core for 24/7 recording.
4.  **Visualization (The Dashboard):** A sub-second latency WebRTC interface built with Streamlit.

---

## Architecture

| Component | File | Tech Stack | Role |
| :--- | :--- | :--- | :--- |
| **Scanner** | scanner.py | Scapy, MacVendor | Finds devices on LAN via ARP. |
| **Connector** | connector.py | ONVIF-Zeep, OpenCV | Extracts RTSP video URLs. |
| **Builder** | config_builder.py | Python | Generates Docker configs. |
| **Core** | docker-compose.yml | Docker, Go2RTC | Streaming server & Recorder. |
| **UI** | app.py | Streamlit | Web-based live viewer. |

---

## Prerequisites

* **OS:** macOS (Apple Silicon supported), Linux (Ubuntu/Debian). Windows supported via WSL2.
* **Docker:** Docker Desktop or Docker Engine installed and running.
* **Python:** Python 3.9+

---

## Installation & Quick Start

### 1. One-Click Setup
Run the included installer to set up the virtual environment (venv) and install system dependencies.

bash
chmod +x setup.sh
./setup.sh
2. Activate Environment
Crucial: You must enter the virtual environment before running any project commands.

Bash

source venv/bin/activate
(You will see (venv) appear in your terminal prompt).

Usage Guide (The 5 Phases)
Phase 1: Discovery (The Hunter)
Scan your local network to identify active IP cameras. Requires root privileges for raw packet generation.

Bash

# Replace 192.168.1.0/24 with your actual subnet
sudo python3 scanner.py -t 192.168.1.0/24
Output: Generates network_map.json

Phase 2: Stream Finding (The Diplomat)
Unlock the video streams for the discovered devices using the "Triple-Key Protocol" (ONVIF -> RTSP Dictionary -> Vendor Hack).

Bash

python3 connector.py
Output: Generates valid_streams.json

Phase 3: Configuration (The Normalizer)
Auto-generate the NVR infrastructure files based on the found streams.

Bash

python3 config_builder.py
Output: Generates go2rtc.yaml and record_streams.sh

Phase 4: Launch Backend
Start the recording engine and streaming server containers.

Bash

docker compose up -d
Verify: Check http://localhost:1984 for the backend status.

Phase 5: Launch Dashboard
Start the visual interface ("Single Pane of Glass").

Bash

streamlit run app.py
Access: Open http://localhost:8501 in your browser.

Interview Demo Guide
Follow these steps to demonstrate the system capabilities during an interview presentation.

1. Preparation

Ensure Docker is running.

Clear old data: rm *.json *.yaml.

Activate environment: source venv/bin/activate.

2. The "Discovery" Demo

Action: Run sudo python3 scanner.py -t <subnet>.

Explanation: "I am using Layer 2 ARP packets to find devices faster than Nmap. Notice how it identifies the Vendor (e.g., Hikvision) via MAC address."

3. The "Intelligence" Demo

Action: Run python3 connector.py.

Explanation: "The system is now negotiating with the cameras. It tries standard ONVIF first, then falls back to a dictionary attack to find the RTSP path."

4. The "Automation" Demo

Action: Run python3 config_builder.py followed by docker compose up -d.

Explanation: "Instead of manually writing config files, my Python script generates the infrastructure code dynamically and spins up the recording engine."

5. The "Visual" Demo

Action: Run streamlit run app.py.

Explanation: "This dashboard uses WebRTC. Unlike standard HLS streams which have 10-second delays, this feed is sub-second real-time."

Tip: If you dont have cameras, enable "Simulation Mode" in the sidebar to show the UI logic.

Project Structure
Plaintext

Universal-NVR/
├── setup.sh            # One-click installer script
├── requirements.txt    # Python library dependencies
├── scanner.py          # Phase 1: Network Discovery Tool
├── connector.py        # Phase 2: Stream Finder Tool
├── config_builder.py   # Phase 3: Config Generator
├── app.py              # Phase 4: Frontend Dashboard
├── docker-compose.yml  # Container Orchestration
├── storage/            # Video Recordings (Mapped Volume)
└── venv/               # Python Virtual Environment
Troubleshooting
1. "Permission Denied" during Scanning ARP scanning requires raw socket access. You must run scanner.py with sudo.

2. Docker: "Bind for 0.0.0.0:1984 failed" Port 1984 is used by Go2RTC. Ensure no other NVR software (like Frigate) is running.

3. "Streamlit: command not found" You forgot to activate the virtual environment. Run source venv/bin/activate.

Shutdown
To stop the system and save resources:

Stop Dashboard: Press Ctrl+C in the terminal running Streamlit.

Stop Backend: Run the following command:

Bash

docker compose down
License
Project created for educational and development purposes.
