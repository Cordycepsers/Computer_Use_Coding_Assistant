# Installation Guide

## System Requirements

- **OS**: Linux, macOS, or Windows with WSL2
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: 20GB+ free space
- **Network**: Internet connection for API calls

## Step-by-Step Installation

### 1. Install Docker

#### Linux
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### macOS
Download and install Docker Desktop from: https://www.docker.com/products/docker-desktop

#### Windows
1. Install WSL2
2. Download Docker Desktop from: https://www.docker.com/products/docker-desktop

### 2. Get Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy the key (starts with `sk-ant-api03-`)

### 3. Extract Package

```bash
unzip computer-use-coding-assistant-*.zip
cd computer-use-coding-assistant-*
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env

# Add your API key
ANTHROPIC_API_KEY=your_actual_key_here
```

### 5. Start Application

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Start all services
./scripts/start.sh
```

### 6. Verify Installation

Open your browser and check:
- http://localhost:8080 - Should show Streamlit UI
- http://localhost:8000/docs - Should show API documentation
- http://localhost:3000 - Should show Grafana login

## Post-Installation

### Change Default Passwords

1. Grafana: Login with admin/admin and change password
2. VNC: Update VNC_PASSWORD in .env

### Configure Monitoring

1. Access Grafana at http://localhost:3000
2. Import dashboards from monitoring/grafana/dashboards/
3. Set up alert channels if needed

### Test the System

```bash
# Test API
curl http://localhost:8000/health

# Test code generation
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "Write hello world in Python"}'
```

## Troubleshooting Installation

### Docker not found
- Ensure Docker is installed and running
- On Linux, logout and login after adding user to docker group

### Ports already in use
- Check for conflicting services: `netstat -tulpn`
- Modify ports in docker-compose.yml

### API key not working
- Verify key format (starts with sk-ant-api03-)
- Check key has credits available
- Ensure no extra spaces in .env file

### Build failures
- Clear Docker cache: `docker system prune -a`
- Rebuild: `docker-compose build --no-cache`
