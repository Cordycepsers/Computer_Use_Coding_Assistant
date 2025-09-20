#!/bin/bash

# Start X virtual framebuffer
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# Start window manager
fluxbox &

# Wait for display to be ready
sleep 2

# Start VNC server
x11vnc -display :99 -forever -usepw -shared -rfbport 5900 &

# Start noVNC
websockify --web=/usr/share/novnc/ 6080 localhost:5900 &

# Start code-server
code-server --bind-addr 0.0.0.0:8443 --auth none &

# Start monitoring collector
cd /home/computeruse/app
python3 monitoring/metrics_collector.py &

# Start FastAPI server
python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload &

# Start Streamlit app
streamlit run api/streamlit_app.py --server.port 8080 --server.address 0.0.0.0 &

# Start Prometheus metrics exporter
python3 monitoring/prometheus_exporter.py &

# Keep container running and show logs
echo "All services started. Container is ready."
echo "Access points:"
echo "  - Streamlit UI: http://localhost:8080"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Code Server: http://localhost:8443"
echo "  - VNC: vnc://localhost:5900"
echo "  - Web VNC: http://localhost:6080/vnc.html"
echo ""
echo "Tailing logs..."

tail -f /home/computeruse/logs/*.log
