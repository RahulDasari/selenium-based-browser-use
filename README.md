# Selenium Bot with Anthropic Claude

A containerized Selenium bot that uses Anthropic's Claude to generate and execute browser automation tasks.

## Quick Start

1. Create a `.env` file with your Anthropic API key:
```
ANTHROPIC_API_KEY=your-key-here
```

2. Build and run with Docker Compose:
```bash
docker-compose up --build
```

## Features
- Automated browser interactions using Selenium
- AI-powered task breakdown using Anthropic Claude
- Conversation state persistence
- Docker containerization with Chrome/Selenium support

## Configuration
- Edit `docker-compose.yml` to modify resource limits or restart policy
- History is persisted in `history.json`
- All dependencies are managed in `requirements.txt`

## Development

To run locally without Docker:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python browser/main.py
```

## Security Notes
- The `.env` file is mounted read-only in the container
- The application runs as a non-root user
- VNC access is password protected (default: seleniumvnc)
- noVNC provides secure HTML5 access

## Viewing the Browser
You can view the browser session in two ways:

1. Using the noVNC web interface:
   - Open http://localhost:8080/vnc.html in your browser
   - Enter the VNC password: seleniumvnc

2. Using a VNC client (optional):
   - Connect to localhost:5900
   - Enter the VNC password: seleniumvnc