import streamlit as st
import cv2
import config
from detector import CrowdDetector
import database
import time
import tempfile
import os

# Page configuration
st.set_page_config(page_title="Crowd Density App", layout="wide", page_icon="👥")

# Initialize database
database.init_db()

# Cache resources so they aren't reloaded every time the user moves a slider
@st.cache_resource
def get_detector():
    return CrowdDetector()

@st.cache_resource
def get_camera():
    # Attempt to open webcam 0
    return cv2.VideoCapture(0)

# Apply custom CSS for styling
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .metric-box {
        background-color: #262730;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .risk-NORMAL { color: #00FF00; }
    .risk-LOW { color: #FFFF00; }
    .risk-MEDIUM { color: #FFA500; }
    .risk-HIGH { color: #FF0000; }
    </style>
""", unsafe_allow_html=True)

st.title("👥 AI Crowd Density Monitor")
st.markdown("Real-time crowd analysis and alert system.")

# Sidebar Settings
st.sidebar.header("⚙️ Configuration")

st.sidebar.subheader("Detection")
config.CONFIDENCE_THRESHOLD = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.3, 0.05)

st.sidebar.subheader("Alert Thresholds")
config.RISK_LOW = st.sidebar.number_input("Low Risk Threshold", min_value=1, value=10)
config.RISK_MEDIUM = st.sidebar.number_input("Medium Risk Threshold", min_value=1, value=20)
config.RISK_HIGH = st.sidebar.number_input("High Risk Threshold", min_value=1, value=35)

# Main UI layout
tab1, tab2 = st.tabs(["Live Monitor", "History Dashboard"])

with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Live Feed")
        
        # Deployment fallback: Allow uploading a video
        uploaded_video = st.file_uploader("Or upload a video file (Cloud Deployment Fallback)", type=['mp4', 'avi', 'mov'])
        
        run_stream = st.checkbox("🟢 Start Stream", value=False)
        frame_window = st.image([])
    
    with col2:
        st.subheader("Live Metrics")
        metric_placeholder = st.empty()
    
    detector = get_detector()
    
    # Use uploaded video if provided, else webcam
    if uploaded_video is not None:
        # Save to temp file
        tfile = tempfile.NamedTemporaryFile(delete=False) 
        tfile.write(uploaded_video.read())
        camera = cv2.VideoCapture(tfile.name)
    else:
        camera = get_camera()

    # Process video loop
    if run_stream:
        if not camera.isOpened():
            st.error("Error: Could not access the webcam.")
        else:
            last_zone_count = -1
            last_total_detected = -1
            last_risk_level = ""
            
            while run_stream:
                ret, frame = camera.read()
                if not ret:
                    st.error("Failed to read from webcam.")
                    break
                
                # Resize frame for performance
                frame = cv2.resize(frame, (1024, 768))
                
                # Process frame
                annotated_frame, zone_count, risk_level, total_detected = detector.process_frame(frame)
                
                # Convert BGR (OpenCV) to RGB (Streamlit)
                annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                
                # Display image
                frame_window.image(annotated_frame)
                
                # Log to database every 5 seconds
                current_time = time.time()
                if 'last_log_time' not in st.session_state:
                    st.session_state['last_log_time'] = current_time
                    
                if current_time - st.session_state['last_log_time'] >= 5:
                    database.log_detection(zone_count, total_detected, risk_level)
                    st.session_state['last_log_time'] = current_time
                
                # Update metrics panel ONLY if they changed to stop blinking
                if zone_count != last_zone_count or total_detected != last_total_detected or risk_level != last_risk_level:
                    color_class = "NORMAL"
                    if "LOW" in risk_level: color_class = "LOW"
                    elif "MEDIUM" in risk_level: color_class = "MEDIUM"
                    elif "HIGH" in risk_level: color_class = "HIGH"
                    
                    metric_placeholder.markdown(f"""
                        <div class="metric-box">
                            <h3>Total Detected</h3>
                            <h1>{total_detected}</h1>
                            <hr>
                            <h3>Zone Count</h3>
                            <h1>{zone_count}</h1>
                            <hr>
                            <h3>Status</h3>
                            <h2 class="risk-{color_class}">{risk_level}</h2>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    last_zone_count = zone_count
                    last_total_detected = total_detected
                    last_risk_level = risk_level
    else:
        st.info("Stream is currently stopped. Click 'Start Stream' to begin.")

with tab2:
    st.header("📈 Historical Crowd Analytics")
    st.markdown("View past crowd density trends below.")
    
    # Provide a refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()
        
    df = database.get_historical_data()
    
    if df.empty:
        st.info("No historical data available yet. Start the stream to log data!")
    else:
        st.dataframe(df.sort_values(by="timestamp", ascending=False).head(100), use_container_width=True)
        
        st.subheader("Trend: Zone Count Over Time")
        # Ensure timestamp is the index for a good line chart
        df_chart = df.set_index('timestamp')
        st.line_chart(df_chart[['zone_count', 'total_detected']])
