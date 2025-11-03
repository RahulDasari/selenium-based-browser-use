FROM python:3.11-slim

# Install system dependencies required for Selenium, VNC, and noVNC
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    chromium \
    chromium-driver \
    x11vnc \
    xvfb \
    fluxbox \
    novnc \
    supervisor \
    net-tools \
    procps \
    xterm \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up VNC password and create required directories
RUN mkdir -p ~/.vnc && \
    mkdir -p /var/log/supervisor && \
    x11vnc -storepasswd seleniumvnc ~/.vnc/passwd

# Set up noVNC (clone only if directory doesn't already exist)
RUN mkdir -p /usr/share/novnc && \
    # Clone noVNC only if the directory is missing or empty (avoid cloning into non-empty dir)
    if [ ! -d /usr/share/novnc ] || [ -z "$(ls -A /usr/share/novnc)" ]; then \
        git clone https://github.com/novnc/noVNC.git /usr/share/novnc/ && \
        cd /usr/share/novnc && \
        git checkout v1.4.0 && \
        cp vnc.html index.html ; \
    else \
        echo "/usr/share/novnc already exists and is not empty; skipping git clone" ; \
    fi && \
    if [ ! -f /usr/local/bin/novnc_proxy ]; then \
        # create a small wrapper if the expected novnc_proxy isn't present
        if [ -f /usr/share/novnc/utils/novnc_proxy ]; then \
            ln -s /usr/share/novnc/utils/novnc_proxy /usr/local/bin/novnc_proxy ; \
        elif [ -f /usr/share/novnc/utils/launch.sh ]; then \
            # older versions provide launch.sh — use it as proxy
            ln -s /usr/share/novnc/utils/launch.sh /usr/local/bin/novnc_proxy ; \
        fi ; \
    fi

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY browser/ ./browser/
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY wait-for-vnc.sh /usr/local/bin/wait-for-vnc.sh
RUN chmod +x /usr/local/bin/wait-for-vnc.sh

RUN mkdir -p /app/browser && \
    useradd -m appuser && \
    chown -R appuser:appuser /app ~/.vnc

ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

EXPOSE 8080 5900

USER appuser

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]