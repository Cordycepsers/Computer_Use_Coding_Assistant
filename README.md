# 🤖 Computer Use Coding Assistant

An AI-powered coding assistant that can control your computer, write code, debug issues, and automate development tasks using Claude's Computer Use capabilities.

## 🚀 Features

- **AI Code Generation** - Generate code in any language with natural language descriptions
- **Intelligent Debugging** - Analyze and fix bugs with AI assistance
- **Code Refactoring** - Improve code quality and performance automatically
- **Test Generation** - Create comprehensive test suites
- **Documentation** - Generate API docs, READMEs, and code comments
- **Computer Control** - AI can control desktop, run commands, and use IDEs
- **Full Monitoring** - Production-ready logging, metrics, and alerting

## 📋 Prerequisites

- Docker & Docker Compose
- Anthropic API Key ([Get one here](https://console.anthropic.com/))
- 8GB+ RAM recommended
- 20GB+ free disk space

## 🎯 Quick Start

### 1. Configure API Key

Edit `.env` file and add your Anthropic API key:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...
```

### 2. Start the Application

```bash
./scripts/start.sh
```

### 3. Access the Application

- **Main UI**: http://localhost:8080
- **API Docs**: http://localhost:8000/docs
- **VNC Desktop**: http://localhost:6080/vnc.html
- **Code Server**: http://localhost:8443
- **Grafana**: http://localhost:3000 (admin/admin)

## 📖 Usage

### Via Web Interface

1. Open http://localhost:8080
2. Enter your coding task
3. Select language and preferences
4. Click "Generate Code"
5. View results and download code

### Via API

```python
import requests

response = requests.post(
    "http://localhost:8000/execute",
    json={
        "task": "Create a Python REST API for todo management",
        "context": {"language": "python", "framework": "fastapi"}
    }
)
print(response.json())
```

### Via Command Line

```bash
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{"task": "Write a sorting algorithm in Python"}'
```

## 🛠️ Configuration

### Environment Variables

See `.env` file for all configuration options:
- `ANTHROPIC_API_KEY` - Your API key (required)
- `LOG_LEVEL` - Logging level (INFO, DEBUG, ERROR)
- `VNC_PASSWORD` - VNC access password
- Alert configurations (Email, Slack, PagerDuty)

### Ports

| Service | Port | Description |
|---------|------|-------------|
| Streamlit | 8080 | Main web interface |
| FastAPI | 8000 | REST API |
| VNC | 5900 | VNC desktop access |
| noVNC | 6080 | Web-based VNC |
| Code Server | 8443 | VS Code in browser |
| Grafana | 3000 | Monitoring dashboards |
| Prometheus | 9091 | Metrics |

## 📊 Monitoring

### Accessing Monitoring Tools

- **Grafana**: http://localhost:3000
  - Username: admin
  - Password: admin (change on first login)
- **Prometheus**: http://localhost:9091
- **Jaeger**: http://localhost:16686 (tracing)

### Available Metrics

- Request rate and latency
- Error rates by type
- Task completion times
- System resources (CPU, memory, disk)
- Active sessions

### Alerts

Configure alerts in `.env`:
- Email alerts via SMTP
- Slack webhooks
- PagerDuty integration

## 🔧 Management

### Start Services
```bash
./scripts/start.sh
```

### Stop Services
```bash
./scripts/stop.sh
```

### View Logs
```bash
docker-compose logs -f
```

### Update Application
```bash
./scripts/update.sh
```

### Create Backup
```bash
./scripts/backup.sh
```

### Enter Container
```bash
docker exec -it computer-use-coding bash
```

## 📁 Project Structure

```
computer-use-coding-assistant/
 ──                 
│── agent/             # AI agent logic
│── api/               # FastAPI server
│── monitoring/        # Monitoring tools
├── docker/                # Docker configuration
├── monitoring/            # Monitoring configs
│   ├── grafana/          # Grafana dashboards
│   └── prometheus/       # Prometheus config
├── projects/             # Project files
├── logs/                 # Application logs
├── scripts/              # Utility scripts
├── docker-compose.yml    # Service orchestration
├── .env                  # Configuration
└── README.md            # Documentation
```

## 🐛 Troubleshooting

### API Key Issues
- Verify key in `.env` file
- Check key has sufficient credits
- Ensure key is active

### Port Conflicts
- Modify ports in `docker-compose.yml`
- Check for conflicting services

### Container Issues
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs coding-assistant

# Restart services
docker-compose restart
```

### Performance Issues
- Allocate more Docker resources
- Check system requirements
- Monitor via Grafana dashboards

## 🔒 Security

- Run in isolated Docker environment
- VNC password protected
- API key stored securely
- Automatic log redaction
- Network isolation

## 🤝 Support

- Check logs: `docker-compose logs -f`
- API documentation: http://localhost:8000/docs
- Monitoring dashboard: http://localhost:3000

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built with:
- [Anthropic Claude API](https://www.anthropic.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [Docker](https://www.docker.com/)


