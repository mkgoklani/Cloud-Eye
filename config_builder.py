import json
import os
import sys

# --- CONFIGURATION ---
INPUT_FILE = "valid_streams.json"
GO2RTC_CONFIG_FILE = "go2rtc.yaml"
RECORDING_SCRIPT = "record_streams.sh"
STORAGE_PATH = "/storage"

# Template for the Go2RTC YAML Header
YAML_HEADER = """streams:
"""

# Template for the Recorder Script Header
SCRIPT_HEADER = """#!/bin/sh
# Auto-generated recording loop
# This script will be run by the 'recorder' container

# Wait for Go2RTC to start
echo "Waiting 10s for Go2RTC..."
sleep 10

"""

def load_streams():
    if not os.path.exists(INPUT_FILE):
        print(f"[-] Error: {INPUT_FILE} not found. Complete Phase 2 first.")
        sys.exit(1)
    with open(INPUT_FILE, 'r') as f:
        return json.load(f)

def sanitize_name(vendor, ip):
    """Create a clean camera name like 'Hikvision_192_168_1_50'"""
    clean_vendor = vendor.split(' ')[0].replace(',', '').replace('.', '')
    clean_ip = ip.replace('.', '_')
    return f"{clean_vendor}_{clean_ip}"

def build_configs(devices):
    yaml_content = YAML_HEADER
    script_content = SCRIPT_HEADER
    
    count = 0
    
    for device in devices:
        if 'stream_url' not in device:
            continue
            
        ip = device['ip']
        vendor = device.get('vendor', 'Generic')
        url = device['stream_url']
        
        # 1. Generate Unique Name
        cam_name = sanitize_name(vendor, ip)
        
        # 2. Add to Go2RTC Config
        # Syntax: name: 
        #           - source_url
        #           - ffmpeg source for web (transcode audio to aac if needed)
        yaml_content += f"  {cam_name}:\n"
        yaml_content += f"    - {url}\n"
        # The line below creates a secondary stream for the browser that ensures Audio is AAC
        yaml_content += f"    - ffmpeg:{cam_name}#video=copy#audio=aac\n\n"
        
        # 3. Add to Recording Script
        # We record from the Go2RTC local loopback (127.0.0.1) to reduce load on the camera
        # Segment time: 900 seconds (15 mins)
        script_content += f"mkdir -p {STORAGE_PATH}/{cam_name}\n"
        script_content += (
            f"ffmpeg -nostdin -re -i rtsp://go2rtc:8554/{cam_name} "
            f"-c copy -f segment -segment_time 900 -strftime 1 "
            f"{STORAGE_PATH}/{cam_name}/%Y-%m-%d_%H-%M-%S.mp4 &\n\n"
        )
        
        count += 1

    # Keep the script alive
    script_content += "wait\n"

    # Write Go2RTC YAML
    with open(GO2RTC_CONFIG_FILE, 'w') as f:
        f.write(yaml_content)
    
    # Write Recording Script
    with open(RECORDING_SCRIPT, 'w') as f:
        f.write(script_content)
    
    # Make script executable
    os.chmod(RECORDING_SCRIPT, 0o755)
    
    print(f"[*] Generated config for {count} cameras.")
    print(f"[*] Created {GO2RTC_CONFIG_FILE}")
    print(f"[*] Created {RECORDING_SCRIPT}")

if __name__ == "__main__":
    devices = load_streams()
    build_configs(devices)