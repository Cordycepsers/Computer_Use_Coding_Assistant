#!/bin/bash

echo "Starting Computer Use Coding Assistant..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Load environment variables
source .env

# Check if API key is configured
if [ "$ANTHROPIC_API_KEY" = "your_api_key_here" ]; then
    echo "Error: Please set your ANTHROPIC_API_KEY in the .env file"
    exit 1
fi

# Start services
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check service status
docker-compose ps

echo ""
echo "====================================="
echo "Services are starting..."
echo "====================================="
echo "Access points:"
echo "  • Streamlit UI:    http://localhost:8080"
echo "  • API Docs:        http://localhost:8000/docs"
echo "  • Code Server:     http://localhost:8443"
echo "  • VNC Desktop:     vnc://localhost:5900"
echo "  • Web VNC:         http://localhost:6080/vnc.html"
echo "  • Grafana:         http://localhost:3000 (admin/admin)"
echo "  • Prometheus:      http://localhost:9091"
echo "  • Jaeger:          http://localhost:16686"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: ./scripts/stop.sh"
