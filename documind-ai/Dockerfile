FROM python:3.11-slim

# Install system dependencies, desktop virtual display & noVNC
RUN apt-get update && apt-get install -y \
    python3-tk \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    fluxbox \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Automatically redirect root '/' directly to the app viewer
RUN ln -s /usr/share/novnc/vnc.html /usr/share/novnc/index.html

WORKDIR /app

# Copy and install python dependencies
COPY client/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code directly
COPY client/ .

EXPOSE 10000

# Start Xvfb display, fluxbox, Tkinter app, and noVNC auto-connect bridge
CMD Xvfb :1 -screen 0 1200x800x24 & \
    sleep 2 && \
    DISPLAY=:1 fluxbox & \
    DISPLAY=:1 python gui.py & \
    x11vnc -display :1 -nopw -listen localhost -xkb -forever & \
    websockify --web=/usr/share/novnc 10000 localhost:5900
