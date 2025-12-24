import streamlit as st
import requests
import math

# --- CONFIGURATION ---
GO2RTC_API = "http://localhost:1984/api/streams"
GO2RTC_PLAYER = "http://localhost:1984/stream.html"

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Universal NVR Dashboard",
    page_icon="📹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LATENCY EXPLANATION (Constraint Requirement) ---
"""
HOW SUB-SECOND LATENCY IS ACHIEVED:
1. Standard Streamlit/HTML5 video tags use HLS (HTTP Live Streaming) or MP4 progressive download.
   These protocols rely on 'chunking' video into small files (ts segments). 
   The player must buffer 3-4 segments before playing to ensure smoothness. 
   Result: 5-10 seconds of latency.

2. Go2RTC uses WebRTC (Web Real-Time Communication).
   This creates a direct Peer-to-Peer UDP connection between the browser and the server.
   It skips the 'file chunking' process entirely and streams raw packets.
   Result: < 500ms latency (Real-Time).

By using an iframe to the Go2RTC player, we bypass Streamlit's backend 
and let the browser handle this high-speed connection directly.
"""

def get_streams():
    """Fetch active streams from Go2RTC API."""
    try:
        response = requests.get(GO2RTC_API, timeout=2)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        # If Go2RTC isn't running, we return empty so the UI doesn't crash
        return {}
    return {}

def get_simulated_streams():
    """Returns dummy data for the Universal Demo Mode."""
    return {
        "Sim_V380_Entrance": {
            "consumers": ["fake_rtsp_1"],
            "type": "Proprietary (V380)"
        },
        "Sim_Android_Kitchen": {
            "consumers": ["fake_rtsp_2"],
            "type": "ONVIF (Pixel 6)"
        },
        "Sim_VLC_Laptop": {
            "consumers": ["fake_rtsp_3"],
            "type": "Generic (RTSP)"
        }
    }

# --- SIDEBAR CONTROL ---
st.sidebar.title("📡 Universal NVR")
st.sidebar.markdown("---")

# Simulation Toggle
sim_mode = st.sidebar.checkbox("🛠 Simulation Mode", value=False)

# Fetch Data
live_streams = get_streams()
status_text = "🟢 Online" if live_streams else "🔴 Offline (Go2RTC not found)"

if sim_mode:
    # Merge real streams with simulated ones
    dummy_data = get_simulated_streams()
    live_streams.update(dummy_data)
    st.sidebar.info(f"Adding {len(dummy_data)} simulated devices.")

# Sidebar Device List
st.sidebar.subheader("Device Status")
st.sidebar.caption(f"Core Status: {status_text}")

camera_list = list(live_streams.keys())

for cam in camera_list:
    # Try to guess type from name or use default
    cam_type = "Standard RTSP"
    if "Sim_" in cam:
        cam_type = live_streams[cam].get("type", "Simulation")
    
    st.sidebar.markdown(f"**📷 {cam}**")
    st.sidebar.caption(f"└ {cam_type}")

# --- MAIN DASHBOARD ---
st.title("Live Operations Center")

if not camera_list:
    st.warning("No cameras detected. Ensure Go2RTC is running or enable 'Simulation Mode'.")
else:
    # Dynamic Grid Layout
    # We want 2 columns per row for a balanced view
    COLS_PER_ROW = 2
    rows = math.ceil(len(camera_list) / COLS_PER_ROW)
    
    # Iterate through cameras and place them in the grid
    for i in range(0, len(camera_list), COLS_PER_ROW):
        cols = st.columns(COLS_PER_ROW)
        
        # Get the slice of cameras for this row
        row_cams = camera_list[i:i+COLS_PER_ROW]
        
        for idx, cam_name in enumerate(row_cams):
            with cols[idx]:
                st.subheader(f"📍 {cam_name}")
                
                # Construct Player URL
                # mode=webrtc forces the low-latency protocol
                player_url = f"{GO2RTC_PLAYER}?src={cam_name}&mode=webrtc"
                
                # Embedding the IFrame
                # scrolling=no removes scrollbars
                # allow="autoplay" is crucial for auto-starting video
                st.components.v1.iframe(
                    src=player_url,
                    height=350,
                    scrolling=False
                )

# Footer
st.markdown("---")
st.caption("Universal NVR System | Phase 4 | Powered by Python, Go2RTC & WebRTC")