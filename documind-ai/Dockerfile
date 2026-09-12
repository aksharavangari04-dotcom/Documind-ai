FROM python:3.11-slim

# Install system GUI dependencies, virtual display & web VNC bridge
RUN apt-get update && apt-get install -y \
    python3-tk \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    fluxbox \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY client/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY client/ .

# Expose port for Render
EXPOSE 10000

# Start Virtual Display, VNC Server, Web-Bridge and launch gui.py directly
CMD Xvfb :1 -screen 0 1100x750x24 & \
    sleep 2 && \
    DISPLAY=:1 fluxbox & \
    DISPLAY=:1 python gui.py & \
    x11vnc -display :1 -nopw -listen localhost -xkb -ncache 10 -ncache_cr -forever & \
    websockify --web=/usr/share/novnc 10000 localhost:5900
