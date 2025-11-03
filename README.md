# Selenium Bot with Anthropic Claude

A containerized Selenium bot that uses Anthropic's Claude to generate and execute browser automation tasks.

## Quick Start

1. Create a `.env` file with your Anthropic API key:
```
ANTHROPIC_API_KEY=your-key-here
```

## Features
- Automated browser interactions using Selenium
- AI-powered task breakdown using Anthropic Claude
- Conversation state persistence
- Docker containerization with Chrome/Selenium support

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
