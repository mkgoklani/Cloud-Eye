import argparse
import json
import socket
import sys
import os
from datetime import datetime

# specialized networking libraries
try:
    import scapy.all as scapy
except ImportError:
    print("Error: 'scapy' is required. Install it via: pip install scapy")
    sys.exit(1)

try:
    from mac_vendor_lookup import MacLookup
except ImportError:
    print("Error: 'mac_vendor_lookup' is required. Install it via: pip install mac-vendor-lookup")
    sys.exit(1)

# Target Ports for Camera Fingerprinting
TARGET_PORTS = [554, 80, 8000, 37777]

# Known Camera Vendors (normalized to uppercase for comparison)
CAMERA_VENDORS = ['HIKVISION', 'DAHUA', 'ESPRESSIF', 'AXIS', 'AMCREST', 'REOLINK', 'V380']

def get_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Universal NVR Discovery Module")
    parser.add_argument("-t", "--target", dest="target", required=True,
                        help="Target Subnet (e.g., 192.168.1.0/24)")
    return parser.parse_args()

def check_root():
    """Ensure the script is running with root/admin privileges for ARP scanning."""
    try:
        if os.geteuid() != 0:
            print("[-] Permission Denied: ARP scanning requires root privileges.")
            print("    Please run with sudo: sudo python3 scanner.py -t <subnet>")
            sys.exit(1)
    except AttributeError:
        # os.geteuid is only available on Unix. On Windows, we assume the user knows to run as Admin.
        pass

def get_vendor(mac_address, mac_lookup_inst):
    """Resolve MAC address to Vendor Name."""
    try:
        return mac_lookup_inst.lookup(mac_address)
    except Exception:
        return "Unknown"

def scan_ports(ip_address):
    """
    Attempt to connect to specific camera ports with a short timeout.
    Returns a list of open ports.
    """
    open_ports = []
    for port in TARGET_PORTS:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0) # 1 second timeout
        result = sock.connect_ex((ip_address, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    return open_ports

def classify_device(vendor, open_ports):
    """
    Determine the device type based on Vendor and Open Ports.
    """
    vendor_upper = vendor.upper()
    
    # Priority 1: Known Camera Manufacturer
    for brand in CAMERA_VENDORS:
        if brand in vendor_upper:
            return "KNOWN_CAMERA_BRAND"
    
    # Priority 2: Generic Vendor but has RTSP Port (554)
    if 554 in open_ports:
        return "POSSIBLE_CAMERA"
        
    return "GENERIC_DEVICE"

def scan_network(subnet):
    """
    Main Logic: ARP Scan -> Vendor Lookup -> Port Scan -> Classification
    """
    print(f"[*] Starting ARP scan on {subnet}...")
    
    # 1. ARP Scan (Layer 2 Broadcast)
    # We ask "Who has this IP?" to the broadcast MAC address (ff:ff:ff:ff:ff:ff)
    arp_request = scapy.ARP(pdst=subnet)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    
    try:
        # srp sends and receives packets at layer 2
        answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    except PermissionError:
        print("[-] Error: Permission denied during packet sending. Are you root?")
        sys.exit(1)

    devices_list = []
    
    # Initialize MacLookup
    print("[*] Initializing MAC Vendor Database...")
    try:
        mac_lookup = MacLookup()
        # mac_lookup.update_vendors() # Uncomment if you need to update the local DB
    except Exception as e:
        print(f"[-] Warning: Could not initialize vendor lookup: {e}")
        mac_lookup = None

    print(f"[*] Found {len(answered_list)} active devices. Starting fingerprinting...")

    for element in answered_list:
        ip = element[1].psrc
        mac = element[1].hwsrc
        
        # 2. Vendor Identification
        vendor = get_vendor(mac, mac_lookup) if mac_lookup else "Unknown"
        
        # 3. Port Fingerprinting
        print(f"    Scanning ports for {ip} ({vendor})...")
        open_ports = scan_ports(ip)
        
        # 4. Classification
        dev_type = classify_device(vendor, open_ports)
        
        device_info = {
            "ip": ip,
            "mac": mac,
            "vendor": vendor,
            "ports": open_ports,
            "type": dev_type
        }
        devices_list.append(device_info)

    return devices_list

def save_to_json(data, filename="network_map.json"):
    """Save the results to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"[*] Success! Network map saved to {filename}")
    except IOError as e:
        print(f"[-] Error saving file: {e}")

def main():
    check_root()
    args = get_arguments()
    
    results = scan_network(args.target)
    
    save_to_json(results)
    
    # Console Summary
    print("\n--- Scan Summary ---")
    count = 0
    for device in results:
        if device['type'] != "GENERIC_DEVICE":
            count += 1
            print(f"[+] Found {device['type']}: {device['ip']} [{device['vendor']}] Ports: {device['ports']}")
    
    if count == 0:
        print("[-] No cameras found. Check if they are powered on and on the same subnet.")

if __name__ == "__main__":
    main()